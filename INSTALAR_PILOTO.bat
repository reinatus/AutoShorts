@echo off
setlocal
cd /d "%~dp0"
title AutoShorts - Instalar piloto Godot
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\bootstrap_pilot.ps1"
if errorlevel 1 (
  echo.
  echo [ERROR] No se pudo preparar el piloto.
  pause
  exit /b 1
)
echo.
echo Piloto preparado. Ejecuta RENDER_PILOTO.bat.
pause

