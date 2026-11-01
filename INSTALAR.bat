@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title AutoShorts - Instalacion

echo ========================================
echo       AUTOSHORTS STUDIO - INSTALAR
echo ========================================
echo.
echo Se instalaran en esta carpeta:
echo   - entorno Python aislado
echo   - FFmpeg para montar videos
echo   - Piper y una voz espanola local
echo.
echo No se instalaran MoneyPrinterTurbo ni servicios de pago.
echo La primera instalacion descarga aproximadamente 140 MB.
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install_windows.ps1"
if errorlevel 1 goto :error

echo.
echo ========================================
echo Instalacion terminada correctamente.
echo Haz doble clic en INICIAR.bat.
echo ========================================
pause
exit /b 0

:error
echo.
echo [ERROR] No se pudo completar la instalacion.
echo Ejecuta DIAGNOSTICO.bat para ver que componente falta.
pause
exit /b 1
