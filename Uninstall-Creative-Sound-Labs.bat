@echo off
title Creative Sound Labs - Uninstall
cd /d "%~dp0"

echo =====================================================================
echo       CREATIVE SOUND LABS: UNINSTALL SHORTCUTS & CLEANUP
echo =====================================================================
echo.

set "DESKTOP_LNK=%USERPROFILE%\Desktop\Creative Sound Labs G6.lnk"
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Creative Sound Labs"

if exist "%DESKTOP_LNK%" (
    del "%DESKTOP_LNK%"
    echo [+] Removed Desktop shortcut.
)

if exist "%START_MENU%" (
    rmdir /s /q "%START_MENU%"
    echo [+] Removed Start Menu shortcut folder.
)

echo.
echo [+] Creative Sound Labs shortcuts have been removed.
echo [*] You can safely delete or keep this folder at your convenience.
echo.
pause
