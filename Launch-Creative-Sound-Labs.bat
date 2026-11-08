@echo off
title Sound BlasterX G6 Studio Console
cd /d "%~dp0"

where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    start "" py -3 creative_sound_labs_g6.py
    exit /b 0
)

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    start "" python creative_sound_labs_g6.py
    exit /b 0
)

echo [ERROR] Python not found in PATH!
echo Please install Python 3.10+ from https://www.python.org or the Microsoft Store.
pause
