import json

import streamlit as st

from autoshorts.director import build_plan
from autoshorts.mpt import MoneyPrinterTurboClient
from autoshorts.presets import PRESETS, get_preset

st.set_page_config(page_title="AutoShorts", page_icon="🎬", layout="wide")

st.title("AutoShorts")
st.caption("Idea → storyboard → material → voz → subtítulos → MP4 vertical")

with st.sidebar:
    st.header("Canal")
    channel_slug = st.selectbox(
        "Preset",
        list(PRESETS.keys()),
        format_func=lambda slug: PRESETS[slug].name,
    )
    preset = get_preset(channel_slug)
    st.write(f"{preset.min_duration}–{preset.max_duration} s · {preset.scenes} escenas · 9:16")
    st.divider()
    st.header("MoneyPrinterTurbo")
    mpt_url = st.text_input("API", "http://127.0.0.1:8080")
    mpt_key = st.text_input("API key", type="password")

subject = st.text_input(
    "Tema",
    "La isla donde está prácticamente prohibido morir",
)
manual_script = st.text_area(
    "Guion manual (opcional para el tema demo)",
    height=150,
    placeholder="Para cualquier tema nuevo puedes pegar aquí el guion. AutoShorts lo convierte en storyboard.",
)

col1, col2 = st.columns([1, 1])
with col1:
    prepare = st.button("Preparar storyboard", type="primary", use_container_width=True)
with col2:
    generate = st.button("Generar vídeo", use_container_width=True)

if prepare or generate:
    try:
        plan = build_plan(subject, preset, manual_script)
        st.session_state["plan"] = plan
    except Exception as exc:
        st.error(str(exc))

plan = st.session_state.get("plan")
if plan:
    st.subheader("Hook")
    st.info(plan.hook)

    st.subheader("Storyboard")
    for scene in plan.scenes:
        with st.expander(f"Escena {scene.index} · {scene.duration:.0f}s", expanded=True):
            st.write(scene.narration)
            st.caption(f"Visual: {scene.visual_query}")

    with st.expander("Payload para MoneyPrinterTurbo"):
        client = MoneyPrinterTurboClient(mpt_url, mpt_key)
        st.code(json.dumps(client.payload(plan, preset), ensure_ascii=False, indent=2), language="json")

    if generate:
        try:
            client = MoneyPrinterTurboClient(mpt_url, mpt_key)
            with st.spinner("Enviando trabajo a MoneyPrinterTurbo…"):
                result = client.create_video(plan, preset)
            st.success("Trabajo enviado")
            st.json(result)
        except Exception as exc:
            st.error(
                "No he podido conectar con MoneyPrinterTurbo. Comprueba que su API esté arrancada y que la URL/API key sean correctas."
            )
            st.exception(exc)

st.divider()
st.caption("V1 · No publica automáticamente. Revisa los hechos y el vídeo antes de subirlo.")
