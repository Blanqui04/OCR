@echo off
REM Run OCR Viewer Application
echo Starting OCR Viewer Application...

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    python main.py
) else (
    echo Virtual environment not found. Running setup first...
    call setup.bat
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
        python main.py
    ) else (
        echo Setup failed. Please run setup.bat manually.
        pause
    )
)

pause
