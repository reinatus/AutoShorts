@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title AutoShorts - IA local

set "OVMS="
set "SETUPVARS="
for /r "runtime\ovms" %%F in (ovms.exe) do if not defined OVMS set "OVMS=%%F"
for /r "runtime\ovms" %%F in (setupvars.bat) do if not defined SETUPVARS set "SETUPVARS=%%F"
if not defined OVMS (
  echo [ERROR] La IA local no esta instalada.
  echo Ejecuta primero INSTALAR_IA.bat
  pause
  exit /b 1
)
if defined SETUPVARS call "%SETUPVARS%"

if not exist "models\OpenVINO\stable-diffusion-v1-5-int8-ov" (
  echo [ERROR] No encuentro el modelo local.
  echo Ejecuta primero INSTALAR_IA.bat
  pause
  exit /b 1
)

echo ========================================
echo       AUTOSHORTS - IA LOCAL
echo ========================================
echo.
echo Intentando usar la GPU Intel...
echo Si OVMS termina por incompatibilidad, vuelve a ejecutar con CPU usando:
echo INICIAR_IA_CPU.bat
echo.

"%OVMS%" --rest_port 8000 --model_repository_path "%CD%\models" --task image_generation --source_model OpenVINO/stable-diffusion-v1-5-int8-ov --target_device GPU

pause
