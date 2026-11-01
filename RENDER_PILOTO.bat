@echo off
setlocal
cd /d "%~dp0"
title AutoShorts - Render piloto Godot
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\render_pilot.ps1"
if errorlevel 1 (
  echo.
  echo [ERROR] El render no ha terminado correctamente.
  pause
  exit /b 1
)
echo.
echo Resultado: godot_pilot\output\autoshorts_pilot.mp4
pause

