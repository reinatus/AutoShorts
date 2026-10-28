# Descargar e instalar AutoShorts en Windows

## Descarga directa

[Descargar el ZIP funcional](https://github.com/reinatus/AutoShorts/archive/refs/heads/feat/godot-procedural-pilot.zip)

1. Pulsa el enlace y guarda el ZIP.
2. En el Explorador de Windows, pulsa **Extraer todo**. No ejecutes AutoShorts desde dentro del ZIP.
3. Entra en la carpeta extraida.
4. Haz doble clic en **INSTALAR.bat**.
5. Espera a que aparezca **Instalacion terminada correctamente**.
6. Haz doble clic en **INICIAR.bat**.

El navegador se abre solo cuando el panel ya responde. Si el puerto 8501 esta ocupado, se prueba automaticamente otro puerto hasta el 8510.

## Que instala

Todo se instala dentro de la carpeta de AutoShorts:

- Python 3.11 portatil;
- dependencias del panel;
- FFmpeg para montar videos;
- Piper y una voz espanola local.

No instala MoneyPrinterTurbo, no requiere Godot y no activa APIs de pago. La primera ejecucion necesita Internet, descarga aproximadamente 250 MB y puede usar cerca de 1 GB de disco entre herramientas, cache y proyectos.

## Si algo falla

1. Ejecuta **DIAGNOSTICO.bat**.
2. Revisa \`logs\\autoshorts-error.log\`.
3. Comprueba que la carpeta esta extraida en Documentos o Escritorio y que Windows permite escribir en ella.
4. Vuelve a ejecutar **INSTALAR.bat**; las descargas correctas se reutilizan.

## Requisitos

- Windows 10 u 11 de 64 bits.
- Aproximadamente 1 GB libre.
- Internet durante la primera instalacion.
- No se necesita tener Python instalado previamente.
