@echo off
title Transport Fleet & Logistics Management System (FMS) - Launcher
cls
echo ==============================================================================
echo    TRANSPORT FLEET & LOGISTICS MANAGEMENT SYSTEM (FMS)
echo    Chanakya University - School of Engineering
echo    BCA V Semester - Full Stack Development (DAT501)
echo    Student: Pranavraghavendra M R (Reg No: 24UG00220)
echo ==============================================================================
echo.

cd /d "%~dp0"

echo [1/3] Running Django System Check...
python manage.py check
if errorlevel 1 (
    echo [ERROR] Django system check failed. Please check Python environment.
    pause
    exit /b %errorlevel%
)

echo.
echo [2/3] Checking Database Migrations...
python manage.py migrate --noinput

echo.
echo [3/3] Starting Django Development Server on http://127.0.0.1:8000/ ...
echo.
echo ==============================================================================
echo   DEMO CREDENTIALS:
echo   Administrator:     admin    / Admin@123
echo   Fleet Manager:     manager  / Manager@123
echo   Maintenance Staff: mechanic / Mechanic@123
echo   General Staff:     staff    / Staff@123
echo ==============================================================================
echo.
echo Press Ctrl+C in this terminal window to stop the server.
echo.

start http://127.0.0.1:8000/
python manage.py runserver 127.0.0.1:8000
pause
