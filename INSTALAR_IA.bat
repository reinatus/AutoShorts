@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title AutoShorts - Instalar IA local

echo ========================================
echo       AUTOSHORTS - IA LOCAL GRATIS
echo ========================================
echo.
echo Se instalara OpenVINO Model Server 2026.4.0 y se descargara
echo Stable Diffusion 1.5 INT8 optimizado para Intel.
echo El modelo ocupa espacio en disco y la primera descarga puede tardar.
echo.

if not exist "runtime" mkdir runtime
if not exist "runtime\ovms" mkdir runtime\ovms
if not exist "models" mkdir models

set "OVMSZIP=%TEMP%\ovms_windows_2026.4.0.zip"
set "OVMSURL=https://github.com/openvinotoolkit/model_server/releases/download/v2026.4.0/ovms_windows_2026.4.0_python_on.zip"

echo [1/4] Descargando OpenVINO Model Server 2026.4.0...
curl.exe -L --fail --retry 3 --retry-delay 2 "%OVMSURL%" -o "%OVMSZIP%"
if errorlevel 1 goto :download_error

for %%A in ("%OVMSZIP%") do if %%~zA LSS 1000000 (
  echo [ERROR] La descarga de OVMS es demasiado pequena y parece incorrecta.
  goto :download_error
)

echo [2/4] Descomprimiendo motor...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Remove-Item -Recurse -Force 'runtime\ovms\*' -ErrorAction SilentlyContinue; Expand-Archive -Path '%OVMSZIP%' -DestinationPath 'runtime\ovms' -Force"
if errorlevel 1 goto :error

set "OVMS="
set "SETUPVARS="
for /r "runtime\ovms" %%F in (ovms.exe) do if not defined OVMS set "OVMS=%%F"
for /r "runtime\ovms" %%F in (setupvars.bat) do if not defined SETUPVARS set "SETUPVARS=%%F"
if not defined OVMS (
  echo [ERROR] No se encontro ovms.exe en el paquete descargado.
  goto :error
)
if defined SETUPVARS call "%SETUPVARS%"

echo [3/4] Descargando Stable Diffusion 1.5 INT8...
echo La primera vez puede tardar varios minutos.
"%OVMS%" --pull --source_model OpenVINO/stable-diffusion-v1-5-int8-ov --model_repository_path "%CD%\models" --model_name OpenVINO/stable-diffusion-v1-5-int8-ov --task image_generation
if errorlevel 1 goto :error

echo [4/4] Guardando configuracion...
>.env.tmp echo IMAGE_API_URL=http://127.0.0.1:8000
>>.env.tmp echo IMAGE_MODEL=OpenVINO/stable-diffusion-v1-5-int8-ov
if exist .env (
  findstr /V /B "IMAGE_API_URL= IMAGE_MODEL=" .env >> .env.tmp
)
move /Y .env.tmp .env >nul

echo.
echo ========================================
echo IA local instalada correctamente.
echo Coste por imagen: 0 EUR.
echo Ejecuta INICIAR_IA.bat y despues INICIAR.bat.
echo ========================================
pause
exit /b 0

:download_error
echo.
echo [ERROR] No se pudo descargar OVMS desde la release oficial 2026.4.0.
echo Comprueba que Windows permite curl.exe y vuelve a intentarlo.
pause
exit /b 1

:error
echo.
echo [ERROR] No se pudo completar la instalacion de la IA local.
echo Deja esta ventana abierta y pasa una captura del error.
pause
exit /b 1
