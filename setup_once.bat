@echo off
cd /d "%~dp0"

echo.
echo ========================================
echo JobFit Agent Setup
echo Installing backend and frontend dependencies
echo ========================================
echo.

echo [1/2] Setting up backend...
cd /d "%~dp0backend"

if not exist ".venv" (
    python -m venv .venv
)

call .venv\Scripts\activate.bat

python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [2/2] Setting up frontend...
cd /d "%~dp0frontend"

npm install

echo.
echo ========================================
echo Setup finished.
echo.
echo Fast mode:
echo start_all_fast.bat
echo.
echo Embedding mode:
echo start_all_embedding.bat
echo ========================================
echo.

pause