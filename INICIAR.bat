@echo off
setlocal
cd /d "%~dp0"
title AutoShorts

if not exist ".venv\Scripts\python.exe" (
  echo AutoShorts no esta instalado todavia.
  echo Ejecutando instalador...
  call INSTALAR.bat
  if errorlevel 1 exit /b 1
)

echo Abriendo AutoShorts en el navegador...
start "" http://localhost:8501
".venv\Scripts\python.exe" -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501

echo.
echo AutoShorts se ha detenido.
pause
