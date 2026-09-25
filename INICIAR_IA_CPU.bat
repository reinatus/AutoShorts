@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title AutoShorts - IA local CPU

set "OVMS="
set "SETUPVARS="
for /r "runtime\ovms" %%F in (ovms.exe) do if not defined OVMS set "OVMS=%%F"
for /r "runtime\ovms" %%F in (setupvars.bat) do if not defined SETUPVARS set "SETUPVARS=%%F"
if not defined OVMS (
  echo [ERROR] Ejecuta primero INSTALAR_IA.bat
  pause
  exit /b 1
)
if defined SETUPVARS call "%SETUPVARS%"

"%OVMS%" --rest_port 8000 --model_repository_path "%CD%\models" --task image_generation --source_model OpenVINO/stable-diffusion-v1-5-int8-ov --target_device CPU

pause
