@echo off
cd /d "%~dp0"

echo.
echo ========================================
echo Starting JobFit Agent - FAST MODE
echo Backend: http://127.0.0.1:8000
echo Frontend: http://localhost:5173
echo ========================================
echo.

start "JobFit Backend FAST" cmd /k call "%~dp0backend\start_fast.bat"

timeout /t 3 /nobreak >nul

start "JobFit Frontend" cmd /k call "%~dp0frontend\start_frontend.bat"

timeout /t 5 /nobreak >nul

start http://localhost:5173

echo.
echo JobFit Agent is starting...
echo If the browser does not open automatically, visit:
echo http://localhost:5173
echo.

pause