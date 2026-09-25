import json

import streamlit as st

from autoshorts.director import build_plan
from autoshorts.mpt import MoneyPrinterTurboClient
from autoshorts.presets import PRESETS, get_preset

st.set_page_config(page_title="AutoShorts", page_icon="🎬", layout="wide")
st.title("AutoShorts")
st.caption("Idea → storyboard → escenas específicas → vídeo fotorealista → voz → subtítulos → MP4 vertical")

with st.sidebar:
    st.header("Canal")
    channel_slug = st.selectbox("Preset", list(PRESETS.keys()), format_func=lambda slug: PRESETS[slug].name)
    preset = get_preset(channel_slug)
    st.write(f"{preset.min_duration}–{preset.max_duration} s · {preset.scenes} escenas · 9:16")
    st.divider()
    st.header("Motor visual")
    video_source = st.selectbox("Generador", ["wavespeed", "ofox", "volcengine_seedance", "muapi"], index=0)
    st.caption("No se usa stock genérico. Cada escena se genera a partir de un prompt específico.")
    st.divider()
    st.header("MoneyPrinterTurbo")
    mpt_url = st.text_input("API", "http://127.0.0.1:8080")
    mpt_key = st.text_input("API key", type="password")
    if st.button("Comprobar motor", use_container_width=True):
        client = MoneyPrinterTurboClient(mpt_url, mpt_key, video_source)
        st.success("MoneyPrinterTurbo responde") if client.health() else st.error("No hay conexión con MoneyPrinterTurbo")

subject = st.text_input("Tema", "La isla donde está prácticamente prohibido morir")
manual_script = st.text_area("Guion manual (opcional para el tema demo)", height=150, placeholder="Para un tema nuevo pega aquí el guion. AutoShorts lo divide y crea las escenas.")

col1, col2 = st.columns(2)
with col1:
    prepare = st.button("Preparar storyboard", type="primary", use_container_width=True)
with col2:
    generate = st.button("Generar vídeo", use_container_width=True)

if prepare or generate:
    try:
        st.session_state["plan"] = build_plan(subject, preset, manual_script)
    except Exception as exc:
        st.error(str(exc))

plan = st.session_state.get("plan")
if plan:
    st.subheader("Hook")
    st.info(plan.hook)
    if plan.requires_real_footage:
        st.warning("Hay escenas que representan lugares concretos. AutoShorts puede generar una recreación para el montaje, pero están marcadas para sustituirlas por metraje real verificado cuando la imagen deba presentarse como auténtica.")

    st.subheader("Storyboard visual")
    for scene in plan.scenes:
        icon = "🎥 REAL" if scene.visual_mode == "real_footage" else "✨ IA"
        with st.expander(f"Escena {scene.index} · {scene.duration:.0f}s · {icon}", expanded=True):
            st.write(scene.narration)
            st.code(scene.visual_query, language=None)
            if scene.on_screen_label:
                st.caption(f"Etiqueta si se usa la generación: {scene.on_screen_label}")

    client = MoneyPrinterTurboClient(mpt_url, mpt_key, video_source)
    with st.expander("Payload para MoneyPrinterTurbo"):
        st.code(json.dumps(client.payload(plan, preset), ensure_ascii=False, indent=2), language="json")

    if generate:
        try:
            if not client.health():
                raise ConnectionError("MoneyPrinterTurbo no responde. Arranca primero el motor.")
            with st.spinner(f"Generando escenas con {video_source}…"):
                result = client.create_video(plan, preset)
                task_id = client.extract_task_id(result)
                st.session_state["task_id"] = task_id
            st.success(f"Render iniciado · {task_id}")
        except Exception as exc:
            st.error(str(exc))

    task_id = st.session_state.get("task_id")
    if task_id:
        st.subheader("Render")
        st.code(task_id)
        if st.button("Actualizar estado"):
            try:
                st.session_state["task_status"] = client.task(task_id)
            except Exception as exc:
                st.error(str(exc))
        status = st.session_state.get("task_status")
        if status:
            st.json(status)
            for url in client.video_urls(status):
                st.video(url)

st.divider()
st.caption("AutoShorts · vídeo generado por escenas. Revisa hechos, derechos y cualquier recreación antes de publicar.")
