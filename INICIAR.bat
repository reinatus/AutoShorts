@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title AutoShorts Studio

if not exist ".runtime\python-path.txt" (
  echo AutoShorts no esta instalado. Abriendo el instalador...
  call INSTALAR.bat
  if errorlevel 1 exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start_windows.ps1"
if errorlevel 1 (
  echo.
  echo [ERROR] AutoShorts no pudo arrancar.
  echo Ejecuta DIAGNOSTICO.bat y revisa logs\autoshorts-error.log.
  pause
  exit /b 1
)
