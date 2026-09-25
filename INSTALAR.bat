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

rem Prefer Python 3.11 when installed, but do not assume it exists just because py.exe exists.
where py >nul 2>nul
if not errorlevel 1 (
  py -3.11 -c "import sys" >nul 2>nul
  if not errorlevel 1 (
    set "PYEXE=py"
    set "PYARGS=-3.11"
  )
)

rem Fall back to a normal python installation (3.10+).
if not defined PYEXE (
  where python >nul 2>nul
  if not errorlevel 1 (
    python -c "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul
    if not errorlevel 1 set "PYEXE=python"
  )
)

rem py launcher may have another usable 3.x version.
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
  echo.
  echo Si tienes el comando py pero no Python instalado, ejecuta:
  echo     py install 3.11
  echo.
  echo Despues vuelve a ejecutar INSTALAR.bat.
  pause
  exit /b 1
)

echo Python encontrado:
%PYEXE% %PYARGS% --version

echo.
if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Creando entorno virtual...
  %PYEXE% %PYARGS% -m venv .venv
  if errorlevel 1 goto :error
) else (
  echo [1/3] Entorno virtual ya existe.
)

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
)

echo.
echo ========================================
echo Instalacion de AutoShorts terminada.
echo Ejecuta INICIAR.bat
echo ========================================
pause
exit /b 0

:error
echo.
echo [ERROR] La instalacion ha fallado.
echo No se continuara si no existe el entorno virtual.
pause
exit /b 1
