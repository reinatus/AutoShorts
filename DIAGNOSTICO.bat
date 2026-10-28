@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title AutoShorts - Diagnostico
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\doctor.ps1"
echo.
pause
exit /b %errorlevel%
