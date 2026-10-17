# Piloto procedural Godot: arquitectura y presupuesto

## Decisión

Godot es el renderizador visual primario. Cada plano se construye con geometría 2D, partículas, capas, desplazamiento de objetos y cambios de estado calculados por tiempo. No hay imágenes fijas, Ken Burns ni llamadas a una API de vídeo.

```text
plan editorial (8 x 5 s)
        ↓
plantillas procedurales Godot + parámetros de escena
        ↓
AVI determinista 1080x1920, 30 fps, 40 s
        ↓ FFmpeg local
MP4 H.264/AAC
```

La futura integración debe transformar cada `Scene` de Python en parámetros de una plantilla Godot; no debe pedir a un LLM que escriba GDScript sin validación. La narración/TTS y los subtítulos temporizados se incorporarán después de medir este render base.

## Presupuesto estricto

| Componente | Piloto | Coste API |
|---|---:|---:|
| Godot procedural | 40 s | 0,00 USD |
| FFmpeg local | 40 s | 0,00 USD |
| Música sintética local | 40 s | 0,00 USD |
| IA de vídeo | desactivada | 0,00 USD |
| Total medido por servicios | | **0,00 USD** |

No se atribuye coste cero a electricidad, tiempo humano ni conexión a Internet. El presupuesto del proyecto controla gasto variable de proveedores.

La IA de vídeo opcional se admite únicamente como sustitución puntual de un plano. Antes de enviar una petición se debe crear una lista de `CostItem` y llamar a `enforce_budget`. Si la estimación supera 0,50 USD, se aborta antes de contactar al proveedor. Los reintentos también deben presupuestarse. No hay credenciales ni proveedor de pago configurados en el piloto.

Como referencia validada el 17-10-2026, una tarifa de 0,05 USD/s implica 2,00 USD para 40 s, sin contar reintentos: cuatro veces el tope. Con 0,10 USD reservados para otras partes, a esa tarifa caben como máximo 8 s opcionales. El precio debe actualizarse desde la página del proveedor antes de habilitarlo.

## Compatibilidad esperada

El proyecto usa el renderizador `gl_compatibility`, geometría 2D y 30 fps. Es una carga mucho menor que ejecutar un modelo de difusión de vídeo y resulta razonable para Intel Core Ultra 5 125U, iGPU y 16 GB. Esto es una inferencia a partir de los requisitos de Godot; el rendimiento real queda confirmado solo tras ejecutar el piloto en la máquina objetivo.

## Reproducibilidad Windows

1. Ejecutar `INSTALAR_PILOTO.bat`. Descarga Godot 4.7.2 desde la versión oficial y el binario FFmpeg incluido en el wheel de `imageio-ffmpeg` 0.6.0; verifica el SHA-256 de ambos.
2. Ejecutar `RENDER_PILOTO.bat`.
3. Revisar `godot_pilot/output/autoshorts_pilot.mp4` y la salida de `ffprobe`: H.264, 1080x1920, 30 fps y unos 40 s.

Las herramientas se guardan en `.tools` y no modifican el sistema ni requieren privilegios de administrador.

## Límites del piloto

- Es una prueba de render y dirección visual, no un Short publicable: no incluye voz narrada, verificación factual automática ni mezcla musical final.
- El audio es una cama sintética generada por Godot, destinada a verificar que la ruta AVI → MP4 conserva audio.
- El texto del storyboard está fijado en el proyecto; falta el adaptador JSON `ShortPlan` → Godot.
- No se ha usado ni facturado ninguna API de pago.
- MoneyPrinterTurbo continúa disponible en el repositorio, pero el piloto no depende de él.

