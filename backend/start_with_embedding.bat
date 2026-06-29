@echo off
cd /d "%~dp0"

echo.
echo ========================================
echo JobFit Agent Backend - EMBEDDING MODE
echo Embedding: ON
echo ========================================
echo.

if not exist ".venv\Scripts\activate.bat" (
    echo Backend virtual environment not found.
    echo Please run setup_once.bat first.
    pause
    exit /b 1
)

set MODEL_PATH=%~dp0..\models\paraphrase-multilingual-MiniLM-L12-v2

if not exist "%MODEL_PATH%" (
    echo Local embedding model not found:
    echo %MODEL_PATH%
    echo.
    echo Backend will still start, but embedding may fallback to TF-IDF.
    echo You can use start_all_fast.bat if you do not need embedding.
    echo.
)

call .venv\Scripts\activate.bat

set JOBFIT_ENABLE_EMBEDDING=true
set JOBFIT_LOCAL_EMBEDDING_MODEL_PATH=%MODEL_PATH%

uvicorn app.main:app --reload

pause