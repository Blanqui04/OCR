# Automated Setup Script for Professional OCR Viewer
# This script sets up the Python environment and installs dependencies

@echo off
title Professional OCR Viewer - Setup
color 0B
echo.
echo ========================================
echo    Professional OCR Viewer - Setup
echo    Automated Installation Script
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

echo 🔍 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.7+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✅ Python found!
python --version

echo.
echo 🏗️ Creating virtual environment...
if exist ".venv" (
    echo Virtual environment already exists, removing old one...
    rmdir /s /q ".venv"
)

python -m venv .venv
if errorlevel 1 (
    echo ❌ Error: Failed to create virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment created!

echo.
echo 📦 Installing dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Error: Failed to install dependencies
    echo.
    echo Trying to install packages individually...
    ".venv\Scripts\python.exe" -m pip install google-cloud-documentai
    ".venv\Scripts\python.exe" -m pip install Pillow
    ".venv\Scripts\python.exe" -m pip install PyMuPDF
)

echo ✅ Dependencies installed!

echo.
echo 🔧 Testing installation...
".venv\Scripts\python.exe" -c "import tkinter; import fitz; from PIL import Image; from google.cloud import documentai_v1; print('All dependencies imported successfully!')"

if errorlevel 1 (
    echo ❌ Error: Some dependencies failed to import
    echo Please check the error messages above
    pause
    exit /b 1
)

echo ✅ Installation test passed!

echo.
echo ========================================
echo    Setup Complete! 🎉
echo ========================================
echo.
echo Next steps:
echo 1. Configure Google Cloud authentication:
echo    - Install Google Cloud SDK
echo    - Run: gcloud auth application-default login
echo    - Set project: gcloud config set project YOUR_PROJECT_ID
echo.
echo 2. Update configuration in ocr_viewer_app.py:
echo    - Set your project_id
echo    - Set your location (e.g., 'us', 'eu')
echo    - Set your processor_id
echo.
echo 3. Launch the application:
echo    - Double-click OCR_Viewer.bat
echo    - Or run: python launch_ocr_viewer.py
echo.
echo For detailed instructions, see README.md
echo.
pause
