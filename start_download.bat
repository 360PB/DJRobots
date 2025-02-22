@echo off
setlocal EnableDelayedExpansion

:: 设置 ChromeDriver 路径
set "CHROMEDRIVER_PATH=%~dp0chromedriver.exe"

:: 检查 ChromeDriver 是否存在
if not exist "%CHROMEDRIVER_PATH%" (
    echo ChromeDriver not found at: %CHROMEDRIVER_PATH%
    echo Please place chromedriver.exe in the same directory as this script
    pause
    exit /b 1
)
echo 测试代码:
echo .venv\Scripts\python app.py --start-page 1 --end-page 2 --start-index 1

echo 开始下载 ...

.venv\Scripts\python.exe app.py --start-page 30 --end-page 100 --start-index 784

cmd /k
pause