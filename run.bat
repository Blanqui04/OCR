@echo off
REM Script d'execució ràpida per OCR Technical Analyzer

echo ========================================
echo    OCR TECHNICAL ANALYZER
echo    Sistema de Producció
echo ========================================

echo.
echo Activant entorn virtual...
call .venv\Scripts\activate.bat

echo.
echo Opcions d'execució:
echo 1. Test ràpid del sistema
echo 2. Demo amb exemple  
echo 3. Processar documents
echo 4. Només YOLOv8
echo.

set /p choice="Selecciona opció (1-4): "

if "%choice%"=="1" (
    echo Executant test ràpid...
    cd production
    python quick_test.py
    pause
)

if "%choice%"=="2" (
    echo Executant demo...
    cd production
    python demo_production.py
    pause
)

if "%choice%"=="3" (
    echo Processant documents...
    cd production
    python process_documents.py
    pause
)

if "%choice%"=="4" (
    echo Detecció YOLOv8...
    python src\technical_element_detector.py --input production\data\input --confidence 0.3
    pause
)

echo.
echo Execució completada!
pause
