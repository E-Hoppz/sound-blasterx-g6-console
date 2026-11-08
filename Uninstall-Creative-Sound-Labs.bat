@echo off
title Sound BlasterX G6 Studio Console - Uninstall
cd /d "%~dp0"

echo =====================================================================
echo       SOUND BLASTERX G6 CONSOLE: UNINSTALL SHORTCUTS & CLEANUP
echo =====================================================================
echo.

set "DESKTOP_LNK=%USERPROFILE%\Desktop\Sound BlasterX G6 Console.lnk"
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Sound BlasterX G6"

if exist "%DESKTOP_LNK%" (
    del "%DESKTOP_LNK%"
    echo [+] Removed Desktop shortcut.
)

if exist "%START_MENU%" (
    rmdir /s /q "%START_MENU%"
    echo [+] Removed Start Menu shortcut folder.
)

echo.
echo [+] Shortcuts have been cleanly removed.
echo [*] You can keep or delete this folder at your convenience.
echo.
pause
