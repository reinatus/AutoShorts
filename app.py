import os
from pathlib import Path

import streamlit as st

from autoshorts.director import build_plan
from autoshorts.image_generator import LocalImageGenerator, STYLE_PRESETS
from autoshorts.mpt import MoneyPrinterTurboClient
from autoshorts.presets import PRESETS, get_preset

st.set_page_config(page_title="AutoShorts", page_icon="🎬", layout="wide")
st.title("AutoShorts")
st.caption("Un canal · un estilo visual · todas las escenas generadas con la misma dirección artística")

with st.sidebar:
    st.header("Canal")
    channel_slug = st.selectbox("Preset", list(PRESETS.keys()), format_func=lambda slug: PRESETS[slug].name)
    preset = get_preset(channel_slug)
    st.write(f"{preset.min_duration}–{preset.max_duration} s · {preset.scenes} escenas · 9:16")
    st.divider()
    st.header("Estilo visual")
    default_style = preset.visual_style if preset.visual_style in STYLE_PRESETS else list(STYLE_PRESETS)[0]
    style = st.selectbox("Estilo del canal", list(STYLE_PRESETS), index=list(STYLE_PRESETS).index(default_style))
    st.caption("Se aplica exactamente el mismo bloque de estilo, modelo y seed base a todas las escenas.")
    st.divider()
    st.header("Generador local · 0 €")
    image_url = st.text_input("OpenVINO API", os.getenv("IMAGE_API_URL", "http://127.0.0.1:8000"))
    image_model = st.text_input("Modelo", os.getenv("IMAGE_MODEL", "OpenVINO/stable-diffusion-v1-5-int8-ov"))
    if st.button("Comprobar generador", use_container_width=True):
        st.success("Generador local conectado") if LocalImageGenerator(image_url, image_model).health() else st.error("OpenVINO todavía no responde")
    st.divider()
    st.header("Montaje")
    mpt_url = st.text_input("MoneyPrinterTurbo API", "http://127.0.0.1:8080")
    mpt_key = st.text_input("MPT API key", type="password")
    if st.button("Comprobar montaje", use_container_width=True):
        st.success("MoneyPrinterTurbo responde") if MoneyPrinterTurboClient(mpt_url, mpt_key).health() else st.error("MoneyPrinterTurbo no responde")

subject = st.text_input("Tema", "La isla donde está prácticamente prohibido morir")
manual_script = st.text_area("Guion manual (opcional para el tema demo)", height=130)

c1, c2 = st.columns(2)
prepare = c1.button("Preparar storyboard", type="primary", use_container_width=True)
generate_images = c2.button("Generar imágenes", use_container_width=True)

if prepare:
    try:
        st.session_state["plan"] = build_plan(subject, preset, manual_script)
        st.session_state.pop("images", None)
    except Exception as exc:
        st.error(str(exc))

plan = st.session_state.get("plan")
if plan:
    st.subheader("Storyboard")
    st.info(f"Dirección artística bloqueada: {style}")
    for scene in plan.scenes:
        with st.expander(f"Escena {scene.index} · {scene.duration:.0f}s", expanded=True):
            st.write(scene.narration)
            st.caption(scene.visual_query)

    if generate_images:
        generator = LocalImageGenerator(image_url, image_model)
        if not generator.health():
            st.error("El generador OpenVINO no está iniciado. Usa primero ‘Comprobar generador’.")
        else:
            outdir = Path("generated") / channel_slug
            images = []
            progress = st.progress(0)
            try:
                for i, scene in enumerate(plan.scenes):
                    target = outdir / f"scene_{scene.index:02d}.png"
                    generator.generate(scene.visual_query, style, str(target), seed=1337 + scene.index)
                    images.append(str(target))
                    progress.progress((i + 1) / len(plan.scenes))
                st.session_state["images"] = images
                st.success("Todas las escenas se han generado con el mismo estilo.")
            except Exception as exc:
                st.error(f"Error generando la escena {len(images)+1}: {exc}")

    images = st.session_state.get("images", [])
    if images:
        st.subheader("Escenas generadas")
        cols = st.columns(4)
        for i, path in enumerate(images):
            if Path(path).exists():
                cols[i % 4].image(path, caption=f"Escena {i+1}", use_container_width=True)

        if st.button("Montar Short", type="primary", use_container_width=True):
            try:
                client = MoneyPrinterTurboClient(mpt_url, mpt_key)
                if not client.health(): raise ConnectionError("MoneyPrinterTurbo no responde.")
                uploaded = [client.upload_material(path) for path in images]
                result = client.create_video(plan, preset, uploaded)
                st.session_state["task_id"] = client.extract_task_id(result)
                st.success(f"Render iniciado · {st.session_state['task_id']}")
            except Exception as exc:
                st.error(str(exc))

    task_id = st.session_state.get("task_id")
    if task_id:
        client = MoneyPrinterTurboClient(mpt_url, mpt_key)
        if st.button("Actualizar render"):
            try: st.session_state["task_status"] = client.task(task_id)
            except Exception as exc: st.error(str(exc))
        status = st.session_state.get("task_status")
        if status:
            st.json(status)
            for url in client.video_urls(status): st.video(url)

st.divider()
st.caption("Las imágenes se generan localmente. No hay coste por imagen ni se mezclan bancos de imágenes con escenas IA.")
