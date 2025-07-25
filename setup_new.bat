@echo off
REM Setup script for OCR Viewer Application
echo ========================================
echo OCR Viewer Application Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or later from https://python.org
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing dependencies...
if exist "requirements_new.txt" (
    pip install -r requirements_new.txt
) else if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo Installing core dependencies...
    pip install PyMuPDF Pillow google-cloud-documentai reportlab
)

echo.
echo ========================================
echo Setup completed!
echo ========================================
echo.
echo To run the application:
echo 1. Activate the virtual environment: venv\Scripts\activate.bat
echo 2. Run the application: python main.py
echo.
echo Or simply run: run_ocr_viewer.bat
echo.
pause
