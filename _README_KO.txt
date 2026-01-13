https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=878297

[일반] [최종판] AI 이용 무료 만화 번역 가이드
초롱이갤로그로 이동합니다. 2025.11.12 13:48:45스크랩 조회 12251 추천 12 댓글 50
본 설치 설명은  https://github.com/zyddnys/manga-image-translator 기반으로 합니다.

월만갤 파딱이 글 잘라서 여기에 다시 적음





1. 설치 준비



Microsoft C++ 빌드 도구 설치

https://visualstudio.microsoft.com/ko/vs/  



Python 3.10.6 설치

https://www.python.org/downloads/release/python-3106/

(설치할때 반드시 Add Python to PATH 체크)

(3.10.6 버전이 권장됩니다. 이미 다른 버전의 Python이 설치되어 있다면 모두 삭제해 주세요)



Git 설치

https://git-scm.com/downloads







2. 설치 과정



① CMD창 열기

그후 아래 명령어 영어 복붙 후 엔터



② C드라이브 경로

cd /d C:\



③ 깃허브에서 소스 가져오기

git clone https://github.com/zyddnys/manga-image-translator.git



④ 프로젝트 폴더로 이동

cd manga-image-translator



⑤ 가상환경 만들기

python -m venv venv

venv\Scripts\activate

(한줄씩 복사 후 붙여넣기 하세요)



⑥ pytorch및 CUDA 설치

pip install torch==2.8.0+cu128 torchvision==0.23.0+cu128 torchaudio==2.8.0+cu128 --index-url https://download.pytorch.org/whl/cu128



 • CUDA 12.8 이상이면, 위 명령어를 그대로 복붙해서 사용해도 됩니다. (대부분의 NVIDIA 그래픽카드는 12.8 이상입니다)

 • CUDA 버전 확인법: 새로운 CMD 창에서 nvidia-smi 입력후 CUDA version 확인.

 • NIVIDA 그래픽카드인데 CUDA 버전이 낮거나 안뜨면 그래픽 드라이버를 최신 버전으로 업데이트해 보세요

 • AMD 그래픽카드이거나 CUDA 버전이 12.8보다 낮은 경우, https://pytorch.org/get-started/locally/ 로 가서 맞는 버전을 선택해 설치하세요.

 • AMD는 CPU 전용 버전을 설치하면 됩니다.



⑦ 라이브러리 설치

pip install -r requirements.txt

python.exe -m pip install PySide6

(한줄씩 복사 후 붙여넣기 하세요)



⑧ cmd창 종료





✅ 설치 완료

 • 설치 경로 : ‪C:\manga-image-translator







3. 번역 방법



① 아래 설정값 다운로드 후 압축 해제 

 • 개인 설정값 다운로드 URL: https://drive.google.com/drive/folders/1mw9CEsUXTKkrieM_FQl3YGVl-bYU94wE?usp=drive_link

② 압축 해제 후 생성된 manga-image-translator 폴더를 통째로 

    설치 완료된 C드라이브에 그대로 복사 후 붙여넣기(덮어쓰기 필수)



7fed8273b58b6af651ef85e54084757365f64b0c93f6e20141f778c0d4b422



28e98977e68a6ba36cb9d2ed14d7266fb12be8e3723eb134c53641863a0a02326fc5d153dec4b6fbeb88038c0f43fe05e2d0ecb5b8c190fcf42167feaecbf7a195e0c574f397eaef11314604fd3dfcc2

③ .env 파일을 열어 GEMINI API 키와 사용할 GEMINI MODEL을 입력하세요.

    • 예) GEMINI_MODEL=gemini-2.5-pro / GEMINI_API_KEY=AVJWLEFK.........

    • Q. Gemini API 키는 어떻게 얻나요?

       구글링하셔서 검색해 보시기 바랍니다. 그 부분까지 적기에는 글이 너무 길어지네요...

       회원 가입 후 카드 등록을 하면 $300 무료 크레딧이 지급됩니다.

④ Launch.bat 실행

→ "manga" 폴더에 있는 모든 파일,폴더가 자동으로 번역되어 "manga-translated" 폴더에 저장됩니다.







4. 주로 사용하는 수치 조정



① 폰트 크기 및 글자 렌더링 관련



깃허브 공식 가로 읽기 전용 manga2eng 렌더러는 텍스트 크기 조절 기능을 지원하지 않습니다.

하지만 필자가 Gemini 2.5 Pro의 도움을 받아 직접 소스 코드를 수정하여

폰트 크기 조절 및 다양한 기능을 추가하였습니다.



방법:

C:\manga-image-translator\manga_translator\rendering\text_render_pillow_eng.py

위 경로의 파일을 메모장으로 열고

ctrl+ f 로 검색



global_font_scale: float = (기본값 0.8)

 • 전체적인 폰트크기. 모든 글자 크기에 전체적으로 적용됩니다.



max_font_size: int = (기본값 150)

 • 값을 줄이면 혼잣말 등 말풍선 밖의 글자 크기는 줄어들 수 있지만, 다른 커야 할 글자의 크기도 너무 작아질 수 있음



sw = max(font.size // 4, 1) = (기본값 4, 1)

 • (8, 1) 이렇게 수정하면 렌더링에서 글씨 주변의 하얀색 테두리(Stroke) 두께가 더 얇아집니다.



line_spacing_px = int(font.size * 0.1) = (기본값 0.1)

 • 0.1 값이 커질수록 렌더링에서 렌더링 시 줄과 줄 사이의 세로 간격(줄 간격) 이 넓어집니다.



word_wrap_ratio = (기본값 1.4)

단어 단위 줄 바꿈을 적용할 기준이 되는 비율을 설정하는 값

수치가 높을 경우:

 • 단어 단위 줄 바꿈 시 말풍선 크기를 그만큼 넓게 계산

 • 말풍선 경계를 넘어갈 수 있음

수치가 낮을 경우:

 • 단어 단위 줄 바꿈 시 말풍선 크기를 그만큼 작게 계산

 • 줄바꿈이 너무 자주 발생하여 가독성이 떨어짐



char_wrap_ratio = (기본값 2.5)

글자 단위 줄 바꿈을 적용할 기준이 되는 비율을 설정하는 값

수치가 높을 경우:

 • 글자 단위 줄 바꿈 시 말풍선 크기를 그만큼 넓게 계산

 • 말풍선 경계를 넘어갈 수 있음

수치가 낮을 경우:

 • 글자 단위 줄 바꿈 시 말풍선 크기를 그만큼 작게 계산

 • 줄바꿈이 너무 자주 발생하여 가독성이 떨어짐





② 텍스트 인식 범위



만화에서 혼잣말, 작은 글씨, 의성어·의태어 등 번역할 텍스트 범위를 지정할 수 있습니다.

 • 값을 낮출수록 → 더 많은 텍스트와 텍스트 박스를 감지

 • 값을 높일수록 → 감지되는 텍스트와 텍스트 박스가 줄어듦

주의:

 • 너무 낮추면 정확도가 떨어지는 텍스트까지 감지되어 노이즈가 증가

 • 너무 높이면 일부 텍스트를 감지하지 못할 수 있음

설정 방법:

config.json → text_threshold, box_threshold = 값 수정

 • GitHub 공식 설정값은 text_threshold = 0.5, box_threshold = 0.7

 • 필요에 따라 수치를 조절하여 취향에 맞게 설정 가능

 • 일반적으로 두 값의 차이를 0~0.2 정도로 맞추는 것이 좋음





③ 사전 기능



전체적인 만화 번역 순서는

텍스트 인식 (Text Detection) → OCR (문자 인식)  → AI 번역  → 렌더링으로 진행.

 • predict = OCR과 AI 번역 사이에서 적용되어, 인식된 원문 텍스트를 교정하는 기능

 • postdict = AI 번역과 렌더링 사이에서 적용되어, 번역된 결과를 교정하는 기능

 • 파일 위치 = C:\manga-image-translator\dict 폴더 내 manga_predict.txt / manga_postdict.txt

 • 왼쪽에는 원본 단어를, 오른쪽에는 교체할 단어를 띄어쓰기 몇 번 뒤에 적기

 • 이 기능은 주로 캐릭터 이름 고정, 특수문자 깨짐 수정, 언니/오빠 같은 어색한 번역 보정 등에 활용됩니다.

 • predict + postdict 혼합 사용으로 특정 문자/단어 번역 제외 방법

     번역에서 특정 텍스트를 완전히 제외하고 싶을 때는 predict와 postdict를 함께 사용합니다.

     먼저 predict에서 번역이 필요 없는 원문을 이모지 같은 임시 기호로 바꾼 뒤,

     postdict에서 번역이 끝난 후 그 이모지를 다시 원래 텍스트로 되돌리면 됩니다.





④ 프롬프트



my_cool_prompt.yaml 파일을 메모장으로 열어 사용자의 취향에 맞게 수정할 수 있습니다.

프롬프트는 번역 품질에 가장 큰 영향을 미치며, 글자가 길수록 높은 토큰값을 사용하여 비용이 증가합니다.

주요 설정:

1. Temperature

 • 0.1 → 안정적, 결정적인 번역 (단조로울 수 있음)

 • 1.0 → 무작위성 ↑, 창의성 ↑ (엉뚱한 번역 가능성 ↑)



2. Chat_system_template

 • AI에게 “어떻게 번역할지” 지시하는 시스템 템플릿

 • 번역 톤, 말투, 처리 방식 등을 여기서 제어 가능



3. Chat_sample

 • AI에게 원하는 번역 형식을 보여주는 예시 샘플

 • 프롬프트 강화에 강력한 역할

 • 2.5 pro사용시에도 어색한 번역이 나올 때, 샘플을 그대로 활용하면 전체 번역 품질 향상







5. 자주 하는 질문



Q. 번역 후 제가 직접 수정(역식)할 수 없나요?



이 툴은 직접 역식하기에는 매우 부적합합니다.

자동 번역 후 직접 손으로 수정하려면 BallonsTranslator가 훨씬 적합합니다.

👉 https://github.com/dmMaze/BallonsTranslator





Q. 번역 속도가 너무 느려요.



원인 1: 그래픽카드 성능이 낮은 경우

원인 2: gemini 2.5-pro 서버 이슈

→ flash 모델을 쓰면 속도는 빨라지지만 품질은 떨어집니다.





Q. server_error_attempt 에러가 계속 떠서 번역이 계속 안되요.



gemini 2.5-pro 서버 이슈입니다. 최근 제미니 API 서버 불안정 문제가 자주 보고되고 있습니다.

잠시 기다렸다가 서버 안정화 후 다시 시도하거나 flash를 이용해보세요.

flash는 왠만해선 서버가 터지는일이 거의없습니다 아주가끔있어요

구글 새 계정을 만들고 카드 등록을 통해 300달러를 받는 신규 유저들은 서버 할당이 적게 배정 된다고 합니다.

경제적인 여유가 되시는 분들은 GPT, Qwen등을 쓰셔도 됩니다.





Q. Microsoft C++ 빌드 도구는 무엇을 설치해야 하나요?



Community 2022 버전 설치 후 계속 "다음"을 누르면 됩니다.





Q. .env, config 파일은 어떻게 열어요?



마우스 우클릭 → 연결 프로그램 → 메모장으로 열면 됩니다.





Q. 일본어 말고 영어, 스페인어 번역도 가능한가요?



my_cool_prompt.yaml을 열어

Do not translate any lines that do not contain Japanese or Chinese words or phrases.

If a line contains both Korean and Japanese or Chinese, always keep the original Korean text and translate the Japanese or Chinese parts into natural Korean that fits the context.

부분에서 Japanese or Chinese 부분을 원하는 번역 언어로 수정해주시면 됩니다.

하지만, 기본적으로 제 프롬프트는 일본어 원서 만화를 번역하기 위해서 최종적으로 깎고 또 깎은거라 

다른 언어를 퀄리티 있게 번역하고 싶다면 프롬프트를 전체적으로 수정이 필요합니다.

현재 chat_sample도 일본어 샘플만 존재합니다.





Q. 여기보다 더 번역 품질을 더 높이는 방법이 있을까요?



1. 2stage OCR

https://github.com/zyddnys/manga-image-translator/pull/973

https://github.com/zyddnys/manga-image-translator/pull/1012

작성자는 현재 결과물에 만족하여 적용하지 않았음 (적용 과정이 다소 번거로움)

2stage 방식은 이미지까지 함께 보내야 하므로 비용이 더 듬



2. Imagetrans

성능은 가장 뛰어나지만 유료이며, 설정이 복잡하고 버그도 많음

https://www.basiccat.org/imagetrans/



3. 참고 자료: 중국 사이트 글 (AI 만화 번역기에 관심 있다면 번역기 돌려서 읽을 만함)

https://zhuanlan.zhihu.com/p/1933214629686907419





Q. 번역 결과물에 □ 같은 특수문자가 나와요.



이는 render가 특정한 문자(예: ⁉)를 인식하지 못해서 발생합니다.

예)

⁉ (한 글자로 인식) → 인식 불가(드래그해보셈)

!? (두 글자로 인식) → 인식 가능(드래그해보셈)

translation_log.txt 로그 파일에서 어떤 특수문자가 문제인지 확인 후, pre-dict에 적절히 매핑해주면 해결됩니다.





Q. 번역할 폴더나 번역 완료 폴더 경로를 변경하고 싶어요. 또한 다른 추가적인 번역 도구 설정도 하고 싶습니다.



https://github.com/zyddnys/manga-image-translator

깃허브 페이지에 여러 다양한 명령어가 정리되어 있으니 참고하시기 바랍니다.

폴더 경로 뿐만 아니라, 중복 파일 덮어씌우기 유무 여부, 저장 파일 유형, 등등 다양한 추가 설정을 할수 있습니다

단, 현재 --save-text 기능은 오류가 있어 사용하지마시고 launch.bat로 번역시 translation_log.txt 메모장 파일로

자동으로 모든 로그가 저장되도록 구현해두었습니다

launcher.ps1 파일을 메모장으로 열어서 수정하세요





Q. launch.bat 실행시 ModuleNotFoundError: No module named ~~ 같은 오류가 뜹니다



기존에 설치된 파이썬을 모두 제거한 뒤, 처음부터 다시 설치를 진행하시고, 파이썬 버전은 반드시 Python 3.10.6로 설치해주세요.

Microsoft C++ 빌드 도구 설치도 제대로 설치 되었는지 확인해주세요.

이 오류는 대부분 위 2개가 제대로 설치되지 않아 requirements.txt 파일이 정상적으로 설치되지 못할 때 발생합니다.





Q. 텍스트/말풍선 인식이 이상해요(필요 없는 작은 글자등 노이즈가 자주 보임). or 의성어 의태어는 번역 안하고싶어요



config.json → text_threshold, box_threshold = 값 수정

위 설명중 4-② 텍스트 인식 범위 참고





Q. 텍스트 인식 결과값이 이상해서 특정 이미지 파일만 다시 제대로 번역하는 방법



1. detector 변경

기본값은 default고 성능도 가장 좋다고 알려져있지만, 특정 이미지에서는 ctd가 더 잘 작동할 수 있습니다.

텍스트 인식 결과가 이상하다면 ctd를 시도해보세요.



2. 임계값 조정

text_threshold와 box_threshold 값을 조정하여 텍스트 인식 민감도를 조절할 수 있습니다.



3. 만화 파일 특성에 맞는 옵션 변경

det_rotate, det_auto_rotate, det_invert, det_gamma_correct 값을 만화 파일에 따라서 false에서 true로 바꿔보세요..

만화 파일에 따라 텍스트 인식 정확도가 달라질 수 있습니다. 일반적으론 false가 기본값입니다





Q. 이름이 일관되지 않게 번역됩니다. 



pre-dict, post-dict 사용. 혹은 프롬프트 Chat_sample 사용





Q. AMD 그래픽카드를 사용하는데 작동이 안 돼요.



2–6 과정에서 PyTorch 및 CUDA를 CPU 버전으로 설치 한 뒤

launcher.ps1 파일을 열고, 실행 옵션 중 --use-gpu 항목을 삭제





Q. 번역이 어색한 부분이 있습니다.



translation_log.txt 파일에서 어색한 번역 부분을 찾아 수정할 문장을 확인

my_cool_prompt.yaml 파일을 열어 해당 문장 혹은 일부 단어를 chat_sample에 등록

chat_sample에 예시를 많이 추가할수록 번역 품질이 향상되지만, 그만큼 토큰 사용량이 늘어납니다





Q. NoneType 관련 에러가 발생합니다.



이 오류는 검열 이슈 또는 서버 문제로 인해 제미니가 결과를 반환하지 못할 때 발생합니다

Flash에서 정상 작동한다면 Pro 서버 문제일 가능성이 높습니다

Flash에서도 동일한 문제가 발생한다면 검열 이슈일 확률이 높습니다

Flash는 품질은 떨어지지만 서버는 안정성이 높아, 서버 장애로 인한 오류가 거의 없습니다

검열 문제는 아주 드물게 매우 엉뚱한 대사에서도 발생할 수 있습니다





Q. 제미니 검열 우회하는 방법



1. 검열 우회 predict / postdict 방식 (간단 정리)

translation_log.txt 확인

→ 검열(차단)이 발생한 페이지를 찾아냅니다.



문제 단어 파악

→ 검열 원인이 된 단어 혹은 문장(예: A)을 확인합니다.



manga_predict에 임시 치환 추가

→ 검열 단어를 임시 이모지예: 😊)로 치환합니다.

# manga_predict 예시

A    😊



manga_postdict에 임시 치환 추가

→ 출력 단계에서 이모지를 원하는 단어로 되돌립니다.

# manga_postdict 예시

😊    (원하는단어)



2. 프롬프트 수정 방식

제가 예전에 올린글에서 어떤 분이 월만갤 댓글에 올린 탈옥 프롬프트를 사용하고,

gemini.py 코드를 약간 수정하면 해결된다고 댓글로 적어주셨는데...

현재 월만갤 완장이 그 글을 짤라서 저도 다시 찾기가 어렵네요.

혹시 해결 방법을 알고 계신 분이 있다면 공유 부탁드립니다.





Q. 인페인팅 결과가 깔끔하지 않아요. 잔여물이 조금씩 남습니다.



내장된 인페인팅 모델 중 깃허브 공식 기준으로 성능이 가장 좋은 모델은 "lama_large" 입니다

단 속도는 가장 느립니다.

필자는 lama_large 사용 시 잔여물이 자주 남아서, 현재는 성능이 좀 떨어지더라도 default 모델을 사용 중입니다

해결 방법을 아시는 분은 댓글로 공유해주시면 감사드립니다

혹은 mask_dilation_offset 값을 높여보는 방법도 있습니다

단, offset 값을 너무 높이면 필요 없는 영역까지 지워질 수 있으므로 주의가 필요합니다





Q. 다른 글꼴로 사용하고 싶어요.



맘에 드는 글꼴 파일을 구글링해서 다운로드한 후,

launcher.ps1 파일을 열어 font-path 경로를 원하는 글꼴 파일 위치로 설정하면 됩니다.





Q. 글자 관련 렌더링 질문 (폰트 크기, 줄바꿈, 줄간격 등)



전체적인 글자 크기, 줄 바꿈, 줄 간격, 최대 글자 크기, 글씨 주변 하얀색 테두리(Stroke) 두께 등 글자 렌더링과 관련된 설정은 

4-① 폰트 크기 및 글자 렌더링 관련에서 확인하고 조정하실 수 있습니다.















좋은 프롬프트가 있으면 댓글로 같이 공유해주세요!!

퀄리티 좋은 predict나 postdict 설정도 같이 공유 부탁!!

질문은 언제든지 환영