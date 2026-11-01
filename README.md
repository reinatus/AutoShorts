# AutoShorts Studio

Herramienta local para organizar varios canales o nichos, mantener un banco de ideas por proyecto y crear Shorts verticales con material real, narracion, subtitulos, cierre, portada y textos de publicacion.

## Descargar e instalar en Windows

[Descargar AutoShorts en ZIP](https://github.com/reinatus/AutoShorts/archive/refs/heads/feat/godot-procedural-pilot.zip)

1. Descarga el ZIP y pulsa **Extraer todo**.
2. Abre la carpeta extraida.
3. Ejecuta **INSTALAR.bat** una sola vez.
4. Ejecuta **INICIAR.bat** cada vez que quieras abrir AutoShorts.

El instalador descarga dentro de la propia carpeta un Python portatil, las dependencias, FFmpeg, Piper y una voz espanola. No exige instalar Python manualmente y no activa APIs de pago. La primera instalacion necesita Internet, descarga aproximadamente 250 MB y puede ocupar cerca de 1 GB al terminar.

Si falla, ejecuta **DIAGNOSTICO.bat**. Consulta tambien [la guia detallada](DESCARGAR_E_INSTALAR.md).

## Que incluye ahora

- cartera con varios proyectos o nichos independientes;
- panel propio para cada proyecto;
- banco de ideas concretas de videos;
- identidad editorial por proyecto;
- presupuesto maximo configurable, con limite objetivo de 0,50 USD;
- generador del documental del pulpo;
- producción automática de 40 segundos: guion, búsqueda y descarga de clips libres, licencias, storyboard, voz, subtítulos, montaje y portada;
- narracion local, subtitulos, gancho, cierre y CTA;
- portada vertical;
- titulo, descripcion, hashtags, palabras clave y lista de publicacion;
- paquete descargable de entregables;
- arranque local sin MoneyPrinterTurbo y sin servicios de pago obligatorios.

## Límites actuales

La ruta automática gratuita busca vídeos reales en Wikimedia Commons y se detiene si no encuentra al menos tres clips relacionados y documentados. No rellena el montaje con imágenes genéricas. La disponibilidad y calidad dependen del archivo libre existente para cada tema; todavía no sustituye una revisión editorial final ni garantiza viralidad. La generación opcional mediante IA de vídeo sigue desactivada hasta que se autorice un proveedor y un presupuesto.

Consulta [Estado del sistema y trabajo pendiente](docs/ESTADO_DEL_SISTEMA.md) para el inventario exacto de lo terminado, lo validado y lo que falta.

## Uso responsable del material

Cada producción guarda un manifiesto con la página de origen, autor y licencia informados por Wikimedia Commons. Revisa ese manifiesto antes de publicar: AutoShorts automatiza la trazabilidad, pero no concede derechos adicionales sobre los vídeos externos.

