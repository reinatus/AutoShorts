# Estado real de AutoShorts

Actualizado: 28 de octubre de 2026.

## Terminado e implementado

- Varios nichos/proyectos, cada uno con su panel, identidad, ideas y entregables.
- Creacion de proyectos desde el panel.
- Banco inicial de ideas de videos por nicho.
- Generacion de guion editorial, titulo, descripcion, hashtags, palabras clave y CTA.
- Limite de coste por Short y bloqueo sobre el presupuesto configurado.
- Flujo documental del pulpo con material real curado.
- Flujo generico de 40 segundos usando tres o mas clips reales aportados por el usuario.
- Narracion local con Piper, subtitulos, apertura, cierre, CTA, portada y paquete de publicacion.
- Instalador Windows autocontenido con Python portatil, FFmpeg y Piper.
- Diagnostico y arranque con espera activa antes de abrir el navegador.
- Sin APIs de pago activadas por defecto.

## Verificado

- Instalacion de Python portatil y 40 dependencias desde una carpeta limpia.
- Descarga y verificacion SHA-256 de uv, Python, FFmpeg, Piper y la voz.
- Diagnostico completo: Python, dependencias, compilacion, FFmpeg, Piper, voz, plantilla, panel y escritura.
- Arranque real del panel y respuesta HTTP 200 en Windows.
- El render del pulpo existente y la logica del panel fueron probados durante el desarrollo anterior.

No se afirma como probado un render completo de cada idea del banco ni todos los equipos Windows posibles.

## Pendiente imprescindible para considerar el sistema terminado

1. **Probar de extremo a extremo varios videos nuevos.** Renderizar, revisar y aprobar al menos tres Shorts de tematicas distintas desde el panel, incluyendo descarga del paquete final.
2. **Biblioteca visual por idea.** Preparar material real especifico, sin repeticiones ni planos genericos, para cada idea prioritaria. Ahora solo el pulpo tiene una ruta curada propia.
3. **Seleccion y derechos del material.** Guardar fuente, licencia y atribucion de cada clip dentro del proyecto antes de permitir publicar.
4. **Revision visual asistida.** Mostrar storyboard y clips elegidos antes del render para sustituir planos incorrectos sin rehacer todo.
5. **Subtitulos y zonas seguras.** Validar posiciones y tamanos en YouTube Shorts, TikTok e Instagram con ejemplos reales.
6. **Calidad de voz.** Ajustar ritmo, pausas, pronunciaciones y normalizacion; Piper funciona, pero la voz sigue siendo sintetica.
7. **Plantillas por identidad.** Convertir colores, tipografias, ritmo, gancho y cierre de cada proyecto en plantillas de render completas, no solo metadatos.
8. **Cola fiable de render.** Cancelar, reintentar, recuperar fallos y limpiar temporales desde el panel.
9. **Pruebas Windows adicionales.** Validar Windows 10 y 11 en un equipo sin Python, con antivirus/SmartScreen y con el puerto 8501 ocupado.
10. **Version descargable estable.** Publicar una version etiquetada o instalador firmado. Por ahora la descarga es un ZIP de la rama funcional.

## Pendiente para una version de produccion

- edicion y duplicado de proyectos;
- historial de versiones de guion y montaje;
- copias de seguridad y migraciones de datos;
- limites y validacion de archivos subidos;
- generacion de portadas mas avanzada que la extraccion/composicion actual;
- metadatos especificos para cada plataforma;
- registro real de costes por proveedor y por video;
- analitica de retencion, rendimiento e iteracion de ideas;
- integraciones de publicacion o programacion;
- modo multiusuario o nube.

## Opcional, solo con autorizacion

- proveedores de IA de video para planos imposibles de conseguir;
- APIs de voz premium;
- generacion de imagenes de portada;
- publicacion automatica.

Cualquier opcion de pago debe permanecer desactivada hasta que el usuario elija proveedor, precio maximo y regla de aprobacion. El objetivo sigue siendo 0,30-0,40 USD por Short y nunca superar 0,50 USD sin autorizacion explicita.
