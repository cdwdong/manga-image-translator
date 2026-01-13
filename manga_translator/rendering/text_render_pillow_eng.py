import re
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import List

from .ballon_extractor import extract_ballon_region
from ..utils import TextBlock
from .text_render_eng import PUNSET_RIGHT_ENG, seg_eng

def merge_seg_eng(
    text: str,
    font,
    bbox_width,
    word_wrap_ratio=1.4,
    char_wrap_ratio=2.5
) -> List[str]:
    """
    주어진 너비에 맞게 텍스트를 여러 줄로 나눕니다.
    외부 tokenizer 대신, 안정적인 '띄어쓰기'를 기준으로 단어를 분리합니다.
    [1단계] 단어 단위로 줄을 나눈 뒤,
    [2단계] 너무 긴 줄만 글자 단위로 잘라냅니다.
    """
    if bbox_width <= 0:
        return [text]

    word_max_width = bbox_width * word_wrap_ratio
    char_max_width = bbox_width * char_wrap_ratio

    # --- ✨✨✨ 핵심 수정: seg_eng() 대신 text.split() 사용 ✨✨✨ ---
    # 이렇게 하면 '토벌'이 '토', '벌'로 쪼개지는 현상이 원천적으로 차단됩니다.
    words = text.split(' ')
    # 혹시 모를 여러 개의 공백으로 인해 생길 수 있는 빈 문자열 제거
    words = [word for word in words if word]
    # -----------------------------------------------------------------

    if not words:
        return []

    # --- 1단계: 단어 단위로 줄 바꿈 수행 ---
    lines = []
    current_line = words[0]
    for i in range(1, len(words)):
        word = words[i]
        test_line = f"{current_line} {word}"
        if font.getlength(test_line) <= word_max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    # 결과 예시: ['조룡 토벌', '후 며칠이 지나']

    # --- 2단계: 너무 긴 줄만 글자 단위로 후처리 ---
    final_lines = []
    for line in lines:
        # 현재 줄이 여전히 너무 길다면 (띄어쓰기 없는 긴 단어)
        if font.getlength(line) > word_max_width:
            sub_line = ""
            for char in line:
                # 글자를 자를 때는 빡빡한 기준(char_max_width)을 사용
                if font.getlength(sub_line + char) > char_max_width:
                    final_lines.append(sub_line)
                    sub_line = char
                else:
                    sub_line += char
            if sub_line:
                final_lines.append(sub_line)
        else:
            # 일반적인 줄은 그냥 추가
            final_lines.append(line)
            
    return final_lines

def widen_mask_opencv_round(mask, width):
    mask_uint8 = mask.astype(np.uint8)
    kernel_size = 2 * width + 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    dilated_mask_uint8 = cv2.dilate(mask_uint8, iterations=1, kernel=kernel)
    return dilated_mask_uint8.astype(bool)


def _check_bbox_collision(b1, b2):
    """Check if two bboxes collide"""
    return not (b1[2] <= b2[0] or b1[0] >= b2[2] or b1[3] <= b2[1] or b1[1] >= b2[3])

def _spiral_points_generator(anchor_x, anchor_y, limit):
    """Generate spiral search points"""
    yield anchor_x, anchor_y
    for radius in range(1, int(limit**0.5)):
        # Top and bottom edges
        for dx in range(-radius, radius+1):
            yield anchor_x + dx, anchor_y - radius
            yield anchor_x + dx, anchor_y + radius
        # Left and right edges (excluding corners)
        for dy in range(-radius+1, radius):
            yield anchor_x - radius, anchor_y + dy
            yield anchor_x + radius, anchor_y + dy

def _find_collision_free_position(bbox_idx, bboxes, anchors, image_bounds, spiral_limit):
    """Find a collision-free position for a bbox"""
    max_x, max_y = image_bounds
    w = bboxes[bbox_idx][2] - bboxes[bbox_idx][0]
    h = bboxes[bbox_idx][3] - bboxes[bbox_idx][1]

    for x, y in _spiral_points_generator(anchors[bbox_idx][0], anchors[bbox_idx][1], spiral_limit):
        candidate = [x, y, x+w, y+h]

        # Check bounds
        if not (0 <= x and 0 <= y and x+w <= max_x and y+h <= max_y):
            continue

        # Check collisions with other boxes
        has_collision = False
        for k, other_bbox in enumerate(bboxes):
            if k != bbox_idx and _check_bbox_collision(candidate, other_bbox):
                has_collision = True
                break

        if not has_collision:
            return candidate

    return None

def solve_collisions_spiral_xyxy(image_shape, initial_bboxes_xyxy, max_iterations=10, spiral_limit=1e5, padding=0):
    """Adjust bounding boxes to avoid overlaps using spiral search"""
    bboxes = [[x1-padding, y1-padding, x2+padding, y2+padding]
              for x1, y1, x2, y2 in initial_bboxes_xyxy]

    if len(bboxes) <= 1:
        return bboxes

    anchors = [(b[0], b[1]) for b in bboxes]

    for _ in range(max_iterations):
        collision_found = False

        for i in range(len(bboxes)):
            for j in range(i+1, len(bboxes)):
                if _check_bbox_collision(bboxes[i], bboxes[j]):
                    collision_found = True
                    new_position = _find_collision_free_position(j, bboxes, anchors, image_shape, spiral_limit)
                    if new_position:
                        bboxes[j] = new_position
                    break

        if not collision_found:
            break

    return bboxes

def render_textblock_list_eng(
    font_path: str,
    img: np.ndarray,
    text_regions: List[TextBlock],
    font_color=(0, 0, 0),
    stroke_color=(255, 255, 255),
    ballonarea_thresh: float = 2,
    downscale_constraint: float = 0.8,
    original_img: np.ndarray = None,
    max_font_size: int = 150,
    bounds_padding: int = 3,
    global_font_scale: float = 0.8
) -> np.ndarray:
    """Render text blocks onto image"""

    def calculate_font_values(font, words, delimiter=' '):
        sw = max(font.size // 8, 1)
        line_height = font.getmetrics()[0] - font.getmetrics()[1]
        delimiter_len = int(font.getlength(delimiter))
        word_lengths = [int(font.getlength(w)) for w in words]
        base_length = max(word_lengths, default=-1)
        return sw, line_height, delimiter_len, base_length, word_lengths

    img_pil = Image.fromarray(img)


    # Initialize enlarge ratios
    for region in text_regions:
        if not hasattr(region, 'enlarge_ratio'):
            region.enlarge_ratio = min(max(region.xywh[2] / region.xywh[3], region.xywh[3] / region.xywh[2]) * 1.5, 3)
        if not hasattr(region, 'enlarged_xyxy'):
            region.enlarged_xyxy = region.xyxy.copy()
            w_diff, h_diff = ((region.xywh[2:] * region.enlarge_ratio - region.xywh[2:]) // 2).astype(int)
            region.enlarged_xyxy[[0,2]] += [-w_diff, w_diff]
            region.enlarged_xyxy[[1,3]] += [-h_diff, h_diff]

    bboxes, rotated_text_layers, sws = [], [], []
    x, y = img.shape[1], img.shape[0]
    for region in text_regions:
        initial_font_size = min(region.font_size, max_font_size)
        font_size = int(initial_font_size * global_font_scale)
        ballon_mask, xyxy = extract_ballon_region(original_img, region.xywh, enlarge_ratio=getattr(region, 'enlarge_ratio', 1))
        if isinstance(xyxy, tuple):
            xyxy = list(xyxy)
        font = ImageFont.truetype(font_path, font_size)
        words = merge_seg_eng(region.translation, font, region.xywh[2])
        if not words:
            continue

        sw, line_height, delimiter_len, base_length, word_lengths = calculate_font_values(font, words)
        ballon_area = (ballon_mask > 0).sum()
        rx, ry = 0, 0

        region.angle = -region.angle
        if abs(region.angle) > 3:
            angle_rad = np.deg2rad(region.angle % 360)
            sin_a, cos_a = np.sin(angle_rad), np.cos(angle_rad)
            ballon_mask = np.array(Image.fromarray(ballon_mask).rotate(region.angle, expand=True))

            if 0 < region.angle <= 90:
                ry = abs(ballon_mask.shape[1] * sin_a)
            elif 90 < region.angle <= 180:
                rx, ry = abs(ballon_mask.shape[1] * cos_a), ballon_mask.shape[0]
            elif 180 < region.angle <= 270:
                rx, ry = ballon_mask.shape[1], abs(ballon_mask.shape[0] * cos_a)
            else:
                rx = abs(ballon_mask.shape[0] * sin_a)

        # Resize if needed
        line_width = sum(word_lengths) + delimiter_len * max(0, len(word_lengths) - 1)
        region_area = line_width * line_height
        area_ratio = ballon_area / max(region_area, 1)

        if area_ratio < ballonarea_thresh:
            resize_ratio = min(np.sqrt(ballonarea_thresh / area_ratio), (1/downscale_constraint)**2)
            rx *= resize_ratio
            ry *= resize_ratio
            ballon_mask = cv2.resize(ballon_mask, None, fx=resize_ratio, fy=resize_ratio)

        # Calculate font size multiplier
        region_x, region_y, region_w, region_h = cv2.boundingRect(cv2.findNonZero(ballon_mask))
        if word_lengths:
            longest_word_idx = max(range(len(word_lengths)), key=lambda i: word_lengths[i])
            base_length_word = words[longest_word_idx]
            if base_length_word:
                lines_needed = len(region.translation) / max(len(base_length_word), 1)
                lines_available = max(1, abs(xyxy[3] - xyxy[1]) // line_height + 1)
                font_size_multiplier = max(min(region_w / (base_length + 2*sw), lines_available / lines_needed), downscale_constraint)

                if font_size_multiplier < 1:
                    font_size = int(font_size * font_size_multiplier)
                    font = ImageFont.truetype(font_path, font_size)
                    words = merge_seg_eng(region.translation, font, region.xywh[2])
                    sw, line_height, delimiter_len, base_length, word_lengths = calculate_font_values(font, words)

        # Create text layer
        bbox_center_x, bbox_center_y = (xyxy[0] + xyxy[2]) / 2, (xyxy[1] + xyxy[3]) / 2
        words_text = '\n'.join(words)
        line_spacing_px = int(font.size * 0.4)
        padding = (font.size + sw) * 4

        # Create temporary layer to measure text size
        temp_img = Image.new('RGBA', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        text_bbox = temp_draw.multiline_textbbox((0, 0), words_text, font=font, spacing=line_spacing_px, align="center")
        text_width = text_bbox[2] - text_bbox[0] + padding
        text_height = text_bbox[3] - text_bbox[1] + padding

        text_layer = Image.new('RGBA', (int(text_width), int(text_height)), (0, 0, 0, 0))
        draw_text = ImageDraw.Draw(text_layer)
        draw_text.multiline_text(
            (text_width // 2, text_height // 2), words_text, font=font,
            fill=font_color, align="center", spacing=line_spacing_px, anchor="mm"
        )

        tx1, ty1, tx2, ty2 = draw_text.textbbox(
            (text_width // 2, text_height // 2), words_text, font=font,
            align="center", spacing=line_spacing_px, anchor="mm"
        )

        rotated_text_layer = text_layer.rotate(region.angle, expand=True, fillcolor=(0, 0, 0, 0))
        rotated_width, rotated_height = rotated_text_layer.size

        # Calculate paste position with bounds checking
        paste_x = bbox_center_x - rotated_width / 2
        paste_y = bbox_center_y - rotated_height / 2

        paste_x = max(bounds_padding - tx1, min(paste_x, x - bounds_padding - tx2))
        paste_y = max(bounds_padding - ty1, min(paste_y, y - bounds_padding - ty2))

        paste_x, paste_y = int(paste_x), int(paste_y)
        bboxes.append([
            [paste_x, paste_y, paste_x + rotated_width, paste_y + rotated_height],
            [paste_x + tx1 - bounds_padding, paste_y + ty1 - bounds_padding,
             paste_x + tx2 + bounds_padding, paste_y + ty2 + bounds_padding]
        ])
        rotated_text_layers.append(rotated_text_layer)
        sws.append(sw)

    # Resolve collisions
    new_bboxes = solve_collisions_spiral_xyxy((x, y), [b[1] for b in bboxes])
    for i, new_bbox in enumerate(new_bboxes):
        offset = [new_bbox[j] - bboxes[i][1][j] for j in range(4)]
        for j in range(4):
            bboxes[i][0][j] += int(offset[j])

    # Apply strokes and paste text
    img_pil = img_pil.convert("RGB")
    img_array = np.array(img_pil)

    for rotated_layer, bbox, sw in zip(rotated_text_layers, bboxes, sws):
        paste_x, paste_y = bbox[0][:2]

        # Create stroke mask
        text_mask = (np.array(rotated_layer).sum(axis=-1) > 0)
        text_mask = widen_mask_opencv_round(text_mask, sw)

        # Clip mask to image bounds
        mask_h, mask_w = text_mask.shape
        y1, y2 = max(0, paste_y), min(y, paste_y + mask_h)
        x1, x2 = max(0, paste_x), min(x, paste_x + mask_w)

        if y2 > y1 and x2 > x1:
            mask_y1 = max(0, -paste_y)
            mask_y2 = mask_y1 + (y2 - y1)
            mask_x1 = max(0, -paste_x)
            mask_x2 = mask_x1 + (x2 - x1)

            img_array[y1:y2, x1:x2][text_mask[mask_y1:mask_y2, mask_x1:mask_x2], :3] = stroke_color

    img_pil = Image.fromarray(img_array)
    for layer, bbox in zip(rotated_text_layers, bboxes):
        img_pil.paste(layer, bbox[0][:2], mask=layer)

    return np.array(img_pil)
