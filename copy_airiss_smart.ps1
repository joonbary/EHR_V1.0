# AIRISS v4 스마트 복사 PowerShell 스크립트

$source = "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"
$destination = "D:\AIRISS_project_clean"

Write-Host "AIRISS v4 스마트 복사 시작..." -ForegroundColor Green
Write-Host "원본: $source"
Write-Host "대상: $destination"
Write-Host ""

# 제외할 폴더 패턴
$excludeDirs = @(
    "node_modules",
    "venv*",
    "__pycache__",
    ".git",
    "cleanup_backup",
    "_archive*",
    "temp*",
    "backup*",
    "logs",
    ".cache"
)

# 대상 폴더 생성
if (Test-Path $destination) {
    Write-Host "기존 폴더 발견. 삭제 중..." -ForegroundColor Yellow
    Remove-Item $destination -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "복사 중... (제외: node_modules, venv, 백업 등)" -ForegroundColor Cyan

# Robocopy 사용 - 더 빠르고 안정적
$excludePattern = $excludeDirs -join " "
$robocopyArgs = @(
    $source,
    $destination,
    "/E",  # 하위 디렉토리 포함
    "/XD", # 디렉토리 제외
    "node_modules", "venv", "venv*", "__pycache__", ".git", "cleanup_backup", "_archive*", "temp*", "backup*", "logs", ".cache",
    "/XF", # 파일 제외
    "*.pyc", "*.pyo", "*.log", "*.tmp",
    "/NFL", # 파일 목록 표시 안함
    "/NDL", # 디렉토리 목록 표시 안함
    "/NJH", # 작업 헤더 표시 안함
    "/NJS", # 작업 요약 표시 안함
    "/NC",  # 파일 클래스 표시 안함
    "/NS",  # 파일 크기 표시 안함
    "/NP"   # 진행률 표시 안함
)

& robocopy @robocopyArgs | Out-Null

if ($LASTEXITCODE -ge 8) {
    Write-Host "복사 중 오류 발생!" -ForegroundColor Red
} else {
    Write-Host "복사 완료!" -ForegroundColor Green
    
    # 복사된 크기 확인
    $size = (Get-ChildItem $destination -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "복사된 크기: $([math]::Round($size, 2)) MB" -ForegroundColor Green
    
    # 설치 가이드 생성
    $guide = @"
# AIRISS v4 설치 가이드

프로젝트가 D:\AIRISS_project_clean으로 복사되었습니다.

## 다음 단계:

### 1. Backend 설정
``````bash
cd D:\AIRISS_project_clean
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
``````

### 2. Frontend 설정
``````bash
cd D:\AIRISS_project_clean\airiss-v4-frontend
npm install
``````

### 3. 서버 실행
``````bash
# Backend
cd D:\AIRISS_project_clean
python app.py

# Frontend (새 터미널)
cd D:\AIRISS_project_clean\airiss-v4-frontend
npm start
``````
"@
    
    $guide | Out-File -FilePath "$destination\SETUP_GUIDE.md" -Encoding UTF8
    
    Write-Host ""
    Write-Host "================================" -ForegroundColor Yellow
    Write-Host "작업 완료!" -ForegroundColor Green
    Write-Host "위치: $destination" -ForegroundColor Green
    Write-Host "설치 가이드: $destination\SETUP_GUIDE.md" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Yellow
}