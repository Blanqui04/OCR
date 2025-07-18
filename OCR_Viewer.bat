@echo off
title Visualitzador Professional d'OCR
color 0A
echo.
echo ========================================
echo    Visualitzador Professional d'OCR v2.0
echo    Integració amb Google Cloud Document AI
echo ========================================
echo.

REM Canvia al directori de l'script
cd /d "%~dp0"

echo 🚀 Iniciant l'aplicació...
echo.

REM Executa l'aplicació utilitzant Python
py ocr_viewer_app.py

echo.
echo 👋 Aplicació tancada.
pause
