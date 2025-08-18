@echo off
echo AIRISS v4 프로젝트 이동 (Robocopy 사용)
echo ============================================================
echo.
echo 원본: C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4
echo 대상: D:\AIRISS_project
echo.
echo 이동을 시작합니다...
echo.

REM 대상 폴더가 있으면 삭제
if exist "D:\AIRISS_project" (
    echo 기존 폴더 삭제 중...
    rmdir /s /q "D:\AIRISS_project"
)

REM Robocopy로 복사 (더 빠르고 안정적)
echo 파일 복사 중... (시간이 걸릴 수 있습니다)
robocopy "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4" "D:\AIRISS_project" /E /MOV /R:1 /W:1

echo.
echo ============================================================
echo 작업 완료!
echo AIRISS v4가 D:\AIRISS_project로 이동되었습니다.
echo ============================================================
pause