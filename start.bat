@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo Starting GitHub Walkthrough Assistant...

python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.10+.
    pause
    exit /b 1
)

echo Server starting at http://127.0.0.1:8010
start http://127.0.0.1:8010

python -m uvicorn src.app:APP --host 127.0.0.1 --port 8010
pause
