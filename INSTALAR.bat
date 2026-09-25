@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title AutoShorts - Instalacion

echo ========================================
echo          AUTOSHORTS - INSTALAR
echo ========================================
echo.

set "PYEXE="
set "PYARGS="
where py >nul 2>nul
if not errorlevel 1 (
  py -3.11 -c "import sys" >nul 2>nul
  if not errorlevel 1 (
    set "PYEXE=py"
    set "PYARGS=-3.11"
  )
)
if not defined PYEXE (
  where python >nul 2>nul
  if not errorlevel 1 (
    python -c "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul
    if not errorlevel 1 set "PYEXE=python"
  )
)
if not defined PYEXE (
  where py >nul 2>nul
  if not errorlevel 1 (
    py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul
    if not errorlevel 1 (
      set "PYEXE=py"
      set "PYARGS=-3"
    )
  )
)
if not defined PYEXE (
  echo [ERROR] No encuentro Python 3.10 o superior instalado.
  echo Ejecuta: py install 3.11
  pause
  exit /b 1
)

echo Python encontrado:
%PYEXE% %PYARGS% --version
if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Creando entorno virtual...
  %PYEXE% %PYARGS% -m venv .venv
  if errorlevel 1 goto :error
) else echo [1/3] Entorno virtual ya existe.
if not exist ".venv\Scripts\python.exe" goto :error

echo [2/3] Actualizando pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :error

echo [3/3] Instalando AutoShorts...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

if not exist ".env" (
  >.env echo MPT_API_URL=http://127.0.0.1:8080
  >>.env echo MPT_API_KEY=
  >>.env echo IMAGE_API_URL=http://127.0.0.1:8000
  >>.env echo IMAGE_MODEL=OpenVINO/stable-diffusion-v1-5-int8-ov
)

echo.
echo ========================================
echo AutoShorts instalado.
echo ========================================
echo.
choice /C SN /N /M "Quieres instalar ahora la IA de imagen local y gratuita? [S/N]: "
if errorlevel 2 goto :done
if errorlevel 1 call INSTALAR_IA.bat

:done
echo.
echo Para usarlo:
echo   1. INICIAR_IA.bat
 echo  2. Arranca MoneyPrinterTurbo
 echo  3. INICIAR.bat
pause
exit /b 0

:error
echo.
echo [ERROR] La instalacion ha fallado.
pause
exit /b 1
