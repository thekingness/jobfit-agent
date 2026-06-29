@echo off
cd /d "%~dp0"

echo.
echo ========================================
echo Starting JobFit Agent - EMBEDDING MODE
echo Backend: http://127.0.0.1:8000
echo Frontend: http://localhost:5173
echo ========================================
echo.

start "JobFit Backend EMBEDDING" cmd /k call "%~dp0backend\start_with_embedding.bat"

timeout /t 3 /nobreak >nul

start "JobFit Frontend" cmd /k call "%~dp0frontend\start_frontend.bat"

timeout /t 5 /nobreak >nul

start http://localhost:5173

echo.
echo JobFit Agent is starting with local embedding model...
echo If the browser does not open automatically, visit:
echo http://localhost:5173
echo.

pause