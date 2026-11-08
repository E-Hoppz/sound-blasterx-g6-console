@echo off
setlocal enabledelayedexpansion
title Sound BlasterX G6 Studio Console Setup
cd /d "%~dp0"

echo =====================================================================
echo       SOUND BLASTERX G6 STUDIO CONSOLE (FOR CREATIVE SB1770)
echo            1-Click Setup ^& Hardware Controller Deployment
echo =====================================================================
echo.

:: 1. Check for Python
echo [*] Checking for Python installation...
set PY_CMD=
where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "PY_CMD=py -3"
    goto :FoundPython
)

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "PY_CMD=python"
    goto :FoundPython
)

echo [!] Python is NOT detected on this system!
echo [*] Attempting automated install or browser download...
echo [*] Opening Python download page...
start https://www.python.org/downloads/
echo.
echo Please install Python 3 (check "Add Python to PATH" during installation)
echo and re-run this setup script.
pause
exit /b 1

:FoundPython
echo [+] Python detected: %PY_CMD%

:: 2. Install requirements
echo [*] Checking / installing Python dependencies (hidapi)...
%PY_CMD% -m pip install --upgrade pip >nul 2>&1
%PY_CMD% -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [!] Warning: pip install encountered an issue. HID control might need manual setup.
) else (
    echo [+] Dependencies installed successfully.
)

:: 3. Create Shortcuts
echo [*] Creating Desktop and Start Menu shortcuts...

set "TARGET_BAT=%~dp0Launch-Creative-Sound-Labs.bat"
set "WORK_DIR=%~dp0"
set "ICON_SRC=shell32.dll,138"

powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'Sound BlasterX G6 Console.lnk')); $s.TargetPath = '%TARGET_BAT%'; $s.WorkingDirectory = '%WORK_DIR%'; $s.IconLocation = '%ICON_SRC%'; $s.Description = 'Sound BlasterX G6 Studio Console (For Creative Labs SB1770)'; $s.Save()"

set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Sound BlasterX G6"
if not exist "%START_MENU%" mkdir "%START_MENU%"

powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%START_MENU%\Sound BlasterX G6 Console.lnk'); $s.TargetPath = '%TARGET_BAT%'; $s.WorkingDirectory = '%WORK_DIR%'; $s.IconLocation = '%ICON_SRC%'; $s.Description = 'Sound BlasterX G6 Studio Console (For Creative Labs SB1770)'; $s.Save()"

echo [+] Shortcuts created:
echo     - Desktop: "Sound BlasterX G6 Console.lnk"
echo     - Start Menu: "%START_MENU%\Sound BlasterX G6 Console.lnk"
echo.
echo =====================================================================
echo                INSTALLATION COMPLETE!
echo =====================================================================
echo.
set /p LAUNCH="Would you like to launch the Studio Console now? (Y/N): "
if /i "%LAUNCH%"=="Y" (
    start "" "%TARGET_BAT%"
)

exit /b 0
