@echo off
title Visualitzador Professional d'OCR
color 0A
echo.
echo ========================================
echo    Visualitzador Professional d'OCR v1.0
echo    Integració amb Google Cloud Document AI
echo ========================================
echo.

REM Canvia al directori de l'script
cd /d "%~dp0"

REM Comprova si existeix l'entorn virtual
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Error: No s'ha trobat l'entorn virtual!
    echo.
    echo Assegura't que la carpeta .venv existeix en aquest directori.
    echo Potser cal que executis la configuració de nou.
    echo.
    pause
    exit /b 1
)

echo 🚀 Iniciant l'aplicació...
echo.

REM Executa l'aplicació utilitzant Python de l'entorn virtual
".venv\Scripts\python.exe" "launch_ocr_viewer.py"

echo.
echo 👋 Aplicació tancada.
pause
