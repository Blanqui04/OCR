@echo off
title Professional OCR Viewer
color 0A
echo.
echo ========================================
echo    Professional OCR Viewer v1.0
echo    Google Cloud Document AI Integration
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Error: Virtual environment not found!
    echo.
    echo Please ensure the .venv folder exists in this directory.
    echo You may need to run the setup again.
    echo.
    pause
    exit /b 1
)

echo 🚀 Starting application...
echo.

REM Run the application using the virtual environment Python
".venv\Scripts\python.exe" "launch_ocr_viewer.py"

echo.
echo 👋 Application closed.
pause
