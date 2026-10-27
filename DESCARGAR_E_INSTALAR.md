# Descargar e instalar AutoShorts en Windows

## Descarga directa

1. Descarga el ZIP de la rama funcional:
   https://github.com/reinatus/AutoShorts/archive/refs/heads/feat/godot-procedural-pilot.zip
2. Pulsa **Extraer todo**. No ejecutes los archivos dentro del ZIP sin extraerlo.
3. Entra en la carpeta extraída.
4. Haz doble clic en **INSTALAR.bat** y espera a que muestre “Instalación terminada correctamente”.
5. Haz doble clic en **INICIAR.bat**.

El navegador se abre únicamente después de que AutoShorts responda correctamente. Si el puerto 8501 está ocupado, el lanzador elige automáticamente otro hasta el 8510.

## Qué instala

Todo queda dentro de la carpeta de AutoShorts, salvo Python si Windows no lo tiene:

- entorno Python aislado;
- panel Streamlit;
- FFmpeg;
- Piper;
- voz española local.

No instala MoneyPrinterTurbo, Godot ni la IA de imágenes para poder usar el panel. Tampoco activa APIs de pago.

## Si algo falla

Ejecuta **DIAGNOSTICO.bat**. Comprueba Python, dependencias, FFmpeg, Piper, voz española, código y permisos de escritura.

Los errores de arranque quedan en:

- `logs\autoshorts-error.log`
- `logs\autoshorts-out.log`

## Requisitos

- Windows 10 u 11 de 64 bits.
- Aproximadamente 1 GB libre para aplicación, herramientas, caché y proyectos.
- Internet durante la primera instalación.
- Python 3.10–3.12. Si falta y `winget` está disponible, el instalador añade Python 3.11 para el usuario actual.
