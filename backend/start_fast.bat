@echo off
cd /d "%~dp0"

echo.
echo ========================================
echo JobFit Agent Backend - FAST MODE
echo Embedding: OFF
echo ========================================
echo.

if not exist ".venv\Scripts\activate.bat" (
    echo Backend virtual environment not found.
    echo Please run setup_once.bat first.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

set JOBFIT_ENABLE_EMBEDDING=false
set JOBFIT_LOCAL_EMBEDDING_MODEL_PATH=

uvicorn app.main:app --reload

pause