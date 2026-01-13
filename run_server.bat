@echo off
title Django Server - Done Dusted
cls
color 0A

echo ==================================================
echo       STARTING DJANGO SERVER...
echo ==================================================
echo.

:: 1. Navigate to Project Directory
cd /d "C:\Users\HP\Desktop\Done-Dusted"

:: 2. Activate Virtual Environment
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating venv...
    call "venv\Scripts\activate.bat"
) else if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating .venv...
    call ".venv\Scripts\activate.bat"
) else if exist "env\Scripts\activate.bat" (
    echo [INFO] Activating env...
    call "env\Scripts\activate.bat"
) else (
    echo [INFO] No virtual environment found.
)

echo.
echo [INFO] Starting Django server...
echo.

:: 3. Run server in background
start cmd /k python manage.py runserver

:: 4. Wait 5 seconds
timeout /t 5 /nobreak >nul

:: 5. Open browser AFTER server starts
echo [INFO] Opening browser...
start http://127.0.0.1:8000/

pause
