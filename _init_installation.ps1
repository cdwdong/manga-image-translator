# manga-translator-setup.ps1
# Manga Image Translator 환경 설정 자동화 스크립트

param(
    [string]$VenvPath = "venv",
    [switch]$Force
)

# 색상 출력 함수
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# 에러 체크 함수
function Test-LastCommand {
    param([string]$ErrorMessage)
    
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "❌ $ErrorMessage" "Red"
        exit 1
    }
}

# 메인 스크립트 시작
Write-ColorOutput "`n🚀 Manga Image Translator 환경 설정 시작`n" "Cyan"

# 1. 기존 가상환경 확인
if (Test-Path $VenvPath) {
    if ($Force) {
        Write-ColorOutput "⚠️  기존 가상환경 삭제 중..." "Yellow"
        Remove-Item -Recurse -Force $VenvPath
    } else {
        Write-ColorOutput "⚠️  기존 가상환경이 존재합니다. -Force 옵션을 사용하여 재생성하거나 삭제 후 다시 실행하세요." "Yellow"
        exit 0
    }
}

# 2. 가상환경 생성
Write-ColorOutput "📦 가상환경 생성 중..." "Green"
python -m venv $VenvPath
Test-LastCommand "가상환경 생성 실패"

# 3. 가상환경 활성화
Write-ColorOutput "🔌 가상환경 활성화 중..." "Green"
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"

if (-not (Test-Path $ActivateScript)) {
    Write-ColorOutput "❌ 활성화 스크립트를 찾을 수 없습니다: $ActivateScript" "Red"
    exit 1
}

& $ActivateScript

# 4. pip 업그레이드
Write-ColorOutput "⬆️  pip 업그레이드 중..." "Green"
python -m pip install --upgrade pip
Test-LastCommand "pip 업그레이드 실패"

# 5. requirements.txt 설치
if (Test-Path ".\requirements.txt") {
    Write-ColorOutput "📋 requirements.txt 설치 중..." "Green"
    pip install -r .\requirements.txt
    Test-LastCommand "requirements.txt 설치 실패"
} else {
    Write-ColorOutput "⚠️  requirements.txt 파일을 찾을 수 없습니다." "Yellow"
}

# 6. PyTorch CUDA 버전 설치
Write-ColorOutput "🔥 PyTorch (CUDA 13.0) 설치 중..." "Green"
pip install torch==2.9.1+cu130 torchvision==0.24.1+cu130 torchaudio==2.9.1+cu130 --index-url https://download.pytorch.org/whl/cu130
Test-LastCommand "PyTorch 설치 실패"

# 7. 설치 확인
Write-ColorOutput "`n✅ 설치 완료! 환경 정보 확인 중...`n" "Cyan"
Write-ColorOutput "Python 버전:" "Yellow"
python --version

Write-ColorOutput "`nPyTorch 버전:" "Yellow"
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'CUDA Version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}')"

Write-ColorOutput "`n🎉 모든 설정이 완료되었습니다!`n" "Green"
Write-ColorOutput "사용법: .\venv\Scripts\Activate.ps1 로 가상환경을 활성화하세요.`n" "Cyan"