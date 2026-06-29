@echo off
cd /d "%~dp0"

echo.
echo ========================================
echo JobFit Agent Frontend
echo URL: http://localhost:5173
echo ========================================
echo.

if not exist "node_modules" (
    echo Frontend dependencies not found.
    echo Please run setup_once.bat first.
    pause
    exit /b 1
)

npm run dev

pause