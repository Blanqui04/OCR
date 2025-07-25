@echo off
REM Run OCR Viewer Application
echo Starting OCR Viewer Application...

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    python main.py
) else (
    echo Virtual environment not found. Running setup first...
    call setup_new.bat
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
        python main.py
    ) else (
        echo Setup failed. Please run setup_new.bat manually.
        pause
    )
)

pause
