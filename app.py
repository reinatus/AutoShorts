import json
import tempfile

import streamlit as st

from autoshorts.director import build_plan
from autoshorts.free_media import best_specific_media, download
from autoshorts.mpt import MoneyPrinterTurboClient
from autoshorts.presets import PRESETS, get_preset

st.set_page_config(page_title="AutoShorts", page_icon="🎬", layout="wide")
st.title("AutoShorts")
st.caption("Shorts con material real específico · sin APIs de vídeo de pago")

with st.sidebar:
    st.header("Canal")
    channel_slug = st.selectbox("Preset", list(PRESETS.keys()), format_func=lambda slug: PRESETS[slug].name)
    preset = get_preset(channel_slug)
    st.write(f"{preset.min_duration}–{preset.max_duration} s · {preset.scenes} escenas · 9:16")
    st.divider()
    st.header("MoneyPrinterTurbo")
    mpt_url = st.text_input("API", "http://127.0.0.1:8080")
    mpt_key = st.text_input("API key", type="password")
    if st.button("Comprobar motor", use_container_width=True):
        st.success("MoneyPrinterTurbo responde") if MoneyPrinterTurboClient(mpt_url, mpt_key).health() else st.error("No hay conexión")

subject = st.text_input("Tema", "La isla donde está prácticamente prohibido morir")
manual_script = st.text_area("Guion manual (opcional para el tema demo)", height=130)

c1, c2 = st.columns(2)
prepare = c1.button("Buscar material y preparar", type="primary", use_container_width=True)
generate = c2.button("Generar vídeo", use_container_width=True)

if prepare:
    try:
        plan = build_plan(subject, preset, manual_script)
        resolved = []
        with st.spinner("Buscando material específico escena por escena…"):
            for scene in plan.scenes:
                # Search with the factual subject plus the scene description. No generic fallback.
                query = f"{subject} {scene.visual_query.split('.')[0]}"
                candidate = best_specific_media(query)
                resolved.append(candidate)
        st.session_state["plan"] = plan
        st.session_state["media"] = resolved
    except Exception as exc:
        st.error(str(exc))

plan = st.session_state.get("plan")
media = st.session_state.get("media", [])
if plan:
    st.subheader("Storyboard y material")
    missing = 0
    for scene, candidate in zip(plan.scenes, media):
        with st.expander(f"Escena {scene.index} · {scene.duration:.0f}s", expanded=True):
            st.write(scene.narration)
            if candidate:
                st.success(f"Encontrado · {candidate.license_name} · relevancia {candidate.score:.2f}")
                st.write(candidate.title)
                if candidate.mime.startswith("image/"): st.image(candidate.url)
                elif candidate.mime.startswith("video/"): st.video(candidate.url)
                st.caption(candidate.page_url)
            else:
                missing += 1
                st.error("Sin material suficientemente específico. No se sustituirá por stock genérico.")

    if missing:
        st.warning(f"Faltan {missing} escenas. El render queda bloqueado hasta tener material relacionado para todas.")

    if generate:
        if missing or len(media) != len(plan.scenes):
            st.error("Primero pulsa ‘Buscar material y preparar’ y resuelve las escenas sin material.")
        else:
            try:
                client = MoneyPrinterTurboClient(mpt_url, mpt_key)
                if not client.health(): raise ConnectionError("MoneyPrinterTurbo no responde.")
                with tempfile.TemporaryDirectory() as tmp:
                    uploaded = []
                    for scene, candidate in zip(plan.scenes, media):
                        local = download(candidate, tmp, f"scene_{scene.index:02d}")
                        uploaded.append(client.upload_material(local))
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
st.caption("Material: fuentes gratuitas con licencia identificada. AutoShorts no usa un recurso si no supera el umbral de relevancia.")
