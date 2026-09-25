# AutoShorts

Fábrica de vídeos verticales 9:16 construida sobre MoneyPrinterTurbo.

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
