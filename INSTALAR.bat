@echo off
setlocal
cd /d "%~dp0"
title AutoShorts - Instalacion

echo ========================================
echo          AUTOSHORTS - INSTALAR
echo ========================================
echo.

where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py -3.11"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo [ERROR] Python no esta instalado.
    echo Instala Python 3.11 y marca "Add Python to PATH".
    pause
    exit /b 1
  )
  set "PY=python"
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Creando entorno virtual...
  %PY% -m venv .venv
  if errorlevel 1 goto :error
) else (
  echo [1/3] Entorno virtual ya existe.
)

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
echo Ahora ejecuta INICIAR.bat
echo ========================================
pause
exit /b 0

:error
echo.
echo [ERROR] La instalacion ha fallado. Copia el mensaje de esta ventana para revisarlo.
pause
exit /b 1
