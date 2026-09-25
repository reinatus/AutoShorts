@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title AutoShorts - Instalar IA local

echo ========================================
echo       AUTOSHORTS - IA LOCAL GRATIS
echo ========================================
echo.
echo Se instalara OpenVINO Model Server 2026.4.0 y se descargara
echo Stable Diffusion 1.5 INT8 optimizado para Intel.
echo.

set "OVMSVER=2026.4.0"
set "OVMSZIP=%TEMP%\ovms_windows_%OVMSVER%.zip"
set "OVMSURL=https://github.com/openvinotoolkit/model_server/releases/download/v%OVMSVER%/ovms_windows_%OVMSVER%_python_on.zip"
set "OVMSROOT=%CD%\runtime\ovms"
set "MODELROOT=%CD%\models"

if not exist "runtime" mkdir "runtime"
if exist "%OVMSROOT%" rmdir /S /Q "%OVMSROOT%"
mkdir "%OVMSROOT%"
if not exist "%MODELROOT%" mkdir "%MODELROOT%"

echo [1/4] Descargando OpenVINO Model Server %OVMSVER%...
curl.exe -L --fail --retry 3 "%OVMSURL%" -o "%OVMSZIP%"
if errorlevel 1 goto :download_error

for %%A in ("%OVMSZIP%") do if %%~zA LSS 50000000 (
  echo [ERROR] El archivo descargado es demasiado pequeno.
  goto :error
)

echo [2/4] Descomprimiendo motor...
tar.exe -xf "%OVMSZIP%" -C "%OVMSROOT%"
if errorlevel 1 goto :error

rem Official archive currently extracts runtime\ovms\ovms\setupvars.bat,
rem but discover it instead of assuming the archive layout.
set "SETUPVARS="
set "OVMSEXE="
for /r "%OVMSROOT%" %%F in (setupvars.bat) do if not defined SETUPVARS set "SETUPVARS=%%~fF"
for /r "%OVMSROOT%" %%F in (ovms.exe) do if not defined OVMSEXE set "OVMSEXE=%%~fF"

if not defined SETUPVARS (
  echo [ERROR] El ZIP se descargo pero no encuentro setupvars.bat.
  goto :show_files
)
if not defined OVMSEXE (
  echo [ERROR] El ZIP se descargo pero no encuentro ovms.exe.
  goto :show_files
)

echo Motor encontrado:
echo   !OVMSEXE!
call "!SETUPVARS!"
if errorlevel 1 goto :error

if not exist "!OVMSEXE!" goto :error

echo [3/4] Descargando Stable Diffusion 1.5 INT8...
echo La primera vez puede tardar varios minutos.
"!OVMSEXE!" --pull --source_model OpenVINO/stable-diffusion-v1-5-int8-ov --model_repository_path "%MODELROOT%" --model_name stable-diffusion-v1-5-int8-ov --task image_generation --target_device GPU
if errorlevel 1 (
  echo.
  echo La descarga/configuracion para GPU no termino. Reintentando para CPU...
  "!OVMSEXE!" --pull --source_model OpenVINO/stable-diffusion-v1-5-int8-ov --model_repository_path "%MODELROOT%" --model_name stable-diffusion-v1-5-int8-ov --task image_generation --target_device CPU
  if errorlevel 1 goto :error
)

echo [4/4] Guardando configuracion...
>.env.tmp echo IMAGE_API_URL=http://127.0.0.1:8000
>>.env.tmp echo IMAGE_MODEL=stable-diffusion-v1-5-int8-ov
if exist .env findstr /V /B /C:"IMAGE_API_URL=" /C:"IMAGE_MODEL=" .env >> .env.tmp
move /Y .env.tmp .env >nul

echo.
echo ========================================
echo IA local instalada correctamente.
echo Coste por imagen: 0 EUR.
echo Ejecuta INICIAR_IA.bat y despues INICIAR.bat.
echo ========================================
pause
exit /b 0

:show_files
echo.
echo Contenido detectado en runtime\ovms:
dir /S /B "%OVMSROOT%" | findstr /I /R "setupvars.bat$ ovms.exe$"
goto :error

:download_error
echo.
echo [ERROR] No se pudo descargar OVMS desde GitHub.
echo URL: %OVMSURL%
pause
exit /b 1

:error
echo.
echo [ERROR] No se pudo completar la instalacion de la IA local.
echo Pasa una captura de las lineas anteriores si vuelve a fallar.
pause
exit /b 1
