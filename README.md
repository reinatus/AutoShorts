# AutoShorts Studio

Aplicación local para gestionar nichos, priorizar ideas, producir Shorts y descargar el paquete completo de publicación.

## Abrir el estudio

1. Haz doble clic en `INSTALAR.bat` la primera vez.
2. Haz doble clic en `INICIAR.bat`.
3. El estudio se abre en `http://localhost:8501`.

La interfaz incluye **Resumen**, **Banco de ideas**, **Crear vídeo**, **Nichos** y **Entregables**. El primer nicho es `Mentes Salvajes`, con 12 ideas editoriales. El vídeo del pulpo dispone ya de render completo; el resto queda bloqueado antes del render hasta incorporar metraje real y fuentes verificadas.

Cada proyecto genera:

- guion y configuración editorial;
- título, descripción, hashtags, palabras clave y CTA;
- lista de comprobaciones para publicar;
- MP4 y portada vertical cuando su renderizador está disponible;
- presupuesto previsto y bloqueo si supera el límite indicado.

La portada de Shorts se genera a 2160×3840. Su disponibilidad de subida depende de las funciones habilitadas en la cuenta y en YouTube Studio.

Fábrica de vídeos verticales 9:16 construida sobre MoneyPrinterTurbo.

> **Piloto nuevo:** la ruta `godot_pilot` genera 40 segundos de animación 2D real, sin imágenes estáticas ni APIs de pago. Consulta [la arquitectura y los límites](docs/ARQUITECTURA_GODOT.md).

## Objetivo

Convertir un canal/preset en una cola de Shorts: idea → hook → guion → storyboard → términos visuales → MoneyPrinterTurbo → MP4.

La V1 incluye:

- Presets de canal persistentes en JSON.
- Canal inicial `lugares-extranos`.
- Storyboard estructurado de 8 escenas.
- Generación de prompts pensados para evitar material genérico.
- Adaptador HTTP para MoneyPrinterTurbo (`POST /api/v1/videos`).
- Cola de trabajos y estado local.
- UI Streamlit sencilla para crear lotes.
- 1080×1920, subtítulos dinámicos y matching de materiales con guion.

## Arquitectura

AutoShorts no sustituye el renderizador. MoneyPrinterTurbo sigue haciendo TTS, búsqueda de material, subtítulos y montaje. AutoShorts añade la capa editorial y de producción masiva.

```text
Canal
  ↓
Tema / ideas
  ↓
Director editorial
  ↓
Hook + guion + storyboard
  ↓
Términos visuales por escena
  ↓
MoneyPrinterTurbo API
  ↓
MP4 1080x1920
```

## Arranque

### Piloto procedural recomendado (Windows)

1. Doble clic en `INSTALAR_PILOTO.bat`.
2. Doble clic en `RENDER_PILOTO.bat`.
3. Abre `godot_pilot\output\autoshorts_pilot.mp4`.

La primera ejecución descarga Godot y FFmpeg de forma local al proyecto. El render base no usa claves ni servicios facturables y aplica un tope de 0,50 USD mediante `autoshorts/budget.py` para futuras extensiones.

### Flujo heredado MoneyPrinterTurbo

1. Arranca MoneyPrinterTurbo y deja su API disponible en `http://127.0.0.1:8080`.
2. Copia `.env.example` a `.env` y configura las claves que quieras usar.
3. Instala dependencias:

```bash
pip install -r requirements.txt
```

4. Inicia AutoShorts:

```bash
streamlit run app.py
```

## Primer canal

`Lugares extraños` está configurado para vídeos de 35–50 segundos, español, 8 escenas, hook inmediato, tono intrigante, montaje rápido, material real prioritario y subtítulos palabra a palabra.

El primer tema sugerido es: `La isla donde está prácticamente prohibido morir`.

## Configuración

- `MPT_API_URL`: URL de MoneyPrinterTurbo.
- `MPT_API_KEY`: opcional si protegiste la API de MPT.
- `OPENAI_API_KEY`: opcional en esta V1. Sin ella AutoShorts puede trabajar con un tema/guion manual; la siguiente capa editorial puede conectarse a un LLM.

No subas `.env` ni `config.toml` con credenciales al repositorio.
