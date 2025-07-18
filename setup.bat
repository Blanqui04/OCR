# Script d'instal·lació automatitzada per al Professional OCR Viewer
# Aquest script configura l'entorn Python i instal·la les dependències

@echo off
title Professional OCR Viewer - Instal·lació
color 0B
echo.
echo ========================================
echo    Professional OCR Viewer - Instal·lació
echo    Script d'instal·lació automatitzada
echo ========================================
echo.

REM Canvia al directori de l'script
cd /d "%~dp0"

echo 🔍 Comprovant la instal·lació de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no està instal·lat o no està al PATH
    echo.
    echo Si us plau, instal·la Python 3.7+ des de: https://www.python.org/downloads/
    echo Assegura't de marcar "Add Python to PATH" durant la instal·lació
    echo.
    pause
    exit /b 1
)

echo ✅ Python trobat!
python --version

echo.
echo 🏗️ Creant l'entorn virtual...
if exist ".venv" (
    echo L'entorn virtual ja existeix, eliminant l'antic...
    rmdir /s /q ".venv"
)

python -m venv .venv
if errorlevel 1 (
    echo ❌ Error: No s'ha pogut crear l'entorn virtual
    pause
    exit /b 1
)

echo ✅ Entorn virtual creat!

echo.
echo 📦 Instal·lant dependències...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Error: No s'han pogut instal·lar les dependències
    echo.
    echo Intentant instal·lar els paquets individualment...
    ".venv\Scripts\python.exe" -m pip install google-cloud-documentai
    ".venv\Scripts\python.exe" -m pip install Pillow
    ".venv\Scripts\python.exe" -m pip install PyMuPDF
)

echo ✅ Dependències instal·lades!

echo.
echo 🔧 Provant la instal·lació...
".venv\Scripts\python.exe" -c "import tkinter; import fitz; from PIL import Image; from google.cloud import documentai_v1; print('Totes les dependències s\'han importat correctament!')"

if errorlevel 1 (
    echo ❌ Error: Algunes dependències no s'han pogut importar
    echo Si us plau, revisa els missatges d'error anteriors
    pause
    exit /b 1
)

echo ✅ Prova d'instal·lació superada!

echo.
echo ========================================
echo    Instal·lació completada! 🎉
echo ========================================
echo.
echo Propers passos:
echo 1. Configura l'autenticació de Google Cloud:
echo    - Instal·la Google Cloud SDK
echo    - Executa: gcloud auth application-default login
echo    - Estableix el projecte: gcloud config set project EL_TEU_PROJECTE_ID
echo.
echo 2. Actualitza la configuració a ocr_viewer_app.py:
echo    - Estableix el teu project_id
echo    - Estableix la teva ubicació (p. ex., 'us', 'eu')
echo    - Estableix el teu processor_id
echo.
echo 3. Llança l'aplicació:
echo    - Fes doble clic a OCR_Viewer.bat
echo    - O executa: python launch_ocr_viewer.py
echo.
echo Per a instruccions detallades, consulta README.md
echo.
pause
