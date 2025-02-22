@echo off
setlocal EnableDelayedExpansion

:: ���� ChromeDriver ·��
set "CHROMEDRIVER_PATH=%~dp0chromedriver.exe"

:: ��� ChromeDriver �Ƿ����
if not exist "%CHROMEDRIVER_PATH%" (
    echo ChromeDriver not found at: %CHROMEDRIVER_PATH%
    echo Please place chromedriver.exe in the same directory as this script
    pause
    exit /b 1
)
echo ���Դ���:
echo .venv\Scripts\python app.py --start-page 1 --end-page 2 --start-index 1

echo ��ʼ���� ...

.venv\Scripts\python.exe app.py --start-page 30 --end-page 100 --start-index 784

cmd /k
pause