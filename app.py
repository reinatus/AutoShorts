from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from autoshorts.studio import Niche, VideoIdea, add_idea, add_niche, create_cover, create_project, ensure_library, list_projects, render_octopus, slugify


ROOT = Path(__file__).resolve().parent
LIBRARY = ROOT / "studio_data"
niches, ideas = ensure_library(LIBRARY)

st.set_page_config(page_title="AutoShorts Studio", page_icon="⚡", layout="wide")
st.markdown("""
<style>
.stApp{background:#07111B;color:#F4F7FA}[data-testid="stSidebar"]{background:#0B1722;border-right:1px solid #23313D}
.hero{padding:1.2rem 1.4rem;border:1px solid #2A3946;border-radius:18px;background:linear-gradient(135deg,#101F2C,#0A141D);margin-bottom:1rem}
.eyebrow{color:#FFD447;font-weight:800;letter-spacing:.12em;font-size:.78rem}.hero h1{margin:.2rem 0;font-size:2.35rem}.muted{color:#A8B3BD}
.score{display:inline-block;background:#FFD447;color:#101820;border-radius:999px;padding:.18rem .6rem;font-weight:800}
div[data-testid="stMetric"]{background:#0E1B26;border:1px solid #263746;padding:1rem;border-radius:14px}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚡ AutoShorts Studio")
    niche_names = {item.slug: item.name for item in niches}
    niche_slug = st.selectbox("Nicho activo", list(niche_names), format_func=niche_names.get)
    active_niche = next(item for item in niches if item.slug == niche_slug)
    st.caption(active_niche.promise)
    st.divider()
    max_cost = st.number_input("Tope por Short (USD)", 0.0, 5.0, 0.50, 0.05)
    st.caption("Ningún proveedor de pago se ejecuta automáticamente.")
    st.divider()
    st.write("**Identidad**")
    st.color_picker("Color de acento", active_niche.primary_color, disabled=True)
    st.caption(active_niche.tone)

st.markdown(f'<div class="hero"><div class="eyebrow">FÁBRICA EDITORIAL LOCAL</div><h1>{active_niche.name}</h1><div class="muted">{active_niche.promise} · Ideas, producción y publicación en un solo lugar.</div></div>', unsafe_allow_html=True)
tab_dashboard, tab_ideas, tab_create, tab_niches, tab_outputs = st.tabs(["Resumen", "Banco de ideas", "Crear vídeo", "Nichos", "Entregables"])
active_ideas = [item for item in ideas if item.niche_slug == niche_slug]

with tab_dashboard:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ideas", len(active_ideas)); c2.metric("Renderizables", sum(item.renderer != "pending" for item in active_ideas)); c3.metric("Coste objetivo", "$0.30–0.40"); c4.metric("Tope", f"${max_cost:.2f}")
    st.subheader("Dirección del canal")
    left, right = st.columns(2)
    left.write(f"**Promesa:** {active_niche.promise}"); left.write(f"**Audiencia:** {active_niche.audience}")
    right.write(f"**Gancho:** {active_niche.hook_formula}"); right.write(f"**Visuales:** {active_niche.visual_policy}")
    st.info("La puntuación viral mide fuerza del gancho, sorpresa, claridad visual y conversación. No garantiza visualizaciones.")

with tab_ideas:
    st.subheader("Ideas priorizadas")
    query = st.text_input("Buscar", placeholder="pulpo, regeneración, sueño…")
    difficulty = st.multiselect("Dificultad visual", ["baja", "media", "alta"], default=["baja", "media", "alta"])
    filtered = [item for item in active_ideas if item.visual_difficulty in difficulty and (not query or query.lower() in (item.title + item.angle).lower())]
    for idea in sorted(filtered, key=lambda item: item.viral_score, reverse=True):
        with st.container(border=True):
            col, action = st.columns([5, 1])
            col.markdown(f"<span class='score'>{idea.viral_score}/100</span> &nbsp; **{idea.title}**", unsafe_allow_html=True)
            col.caption(idea.angle); col.write(f"**Gancho:** {idea.hook}"); col.write(f"**Primer plano:** {idea.visual_hook}")
            col.caption(f"Dificultad {idea.visual_difficulty} · coste previsto ${idea.estimated_cost_usd:.2f} · {idea.status}")
            if action.button("Usar", key=f"use-{idea.slug}", use_container_width=True):
                st.session_state["selected_idea"] = idea.slug; st.toast("Idea enviada a Crear vídeo")
    with st.expander("Añadir una idea"):
        with st.form("new-idea"):
            title = st.text_input("Título de trabajo"); angle = st.text_area("Ángulo"); hook = st.text_input("Gancho"); visual = st.text_input("Primer plano imprescindible"); score = st.slider("Puntuación editorial", 1, 100, 75)
            if st.form_submit_button("Guardar idea"):
                add_idea(LIBRARY, VideoIdea(slugify(title), niche_slug, title, angle, hook, visual, score, "media", 0.0)); st.success("Idea guardada. Recarga para verla.")

with tab_create:
    st.subheader("Crear vídeo")
    selected_slug = st.session_state.get("selected_idea", active_ideas[0].slug)
    choices = {item.slug: item.title for item in active_ideas}
    selected_slug = st.selectbox("Idea", list(choices), index=list(choices).index(selected_slug) if selected_slug in choices else 0, format_func=choices.get)
    idea = next(item for item in active_ideas if item.slug == selected_slug)
    default_script = (ROOT / "real_media" / "octopus" / "narracion.txt").read_text(encoding="utf-8") if idea.renderer == "octopus" else f"{idea.hook}\n\n{idea.angle}\n\n[Cierra con una pregunta que invite a comentar.]"
    script = st.text_area("Guion", default_script, height=240)
    cta_index = st.selectbox("Acción final", range(len(active_niche.cta_variants)), format_func=lambda i: active_niche.cta_variants[i])
    col1, col2 = st.columns(2); col1.write(f"**Política visual:** {active_niche.visual_policy}"); col2.write(f"**Coste previsto:** ${idea.estimated_cost_usd:.2f} / ${max_cost:.2f}")
    blocked = idea.estimated_cost_usd > max_cost
    if blocked: st.error("Esta idea supera el presupuesto y no puede ejecutarse.")
    if st.button("Crear proyecto", type="primary", use_container_width=True, disabled=blocked):
        project = create_project(LIBRARY, idea, active_niche, script, cta_index); st.session_state["current_project"] = str(project); st.session_state["current_idea"] = idea.slug; st.success("Proyecto y paquete de publicación creados.")
    project_value = st.session_state.get("current_project")
    if project_value and st.session_state.get("current_idea") == idea.slug:
        project = Path(project_value); st.caption(f"Proyecto: {project.name}")
        if idea.renderer == "octopus":
            if st.button("Renderizar vídeo final", use_container_width=True):
                with st.spinner("Renderizando localmente. No cierres esta ventana…"):
                    video = render_octopus(ROOT, project, cta_index); cover = create_cover(ROOT, video, project / "portada-9x16.jpg")
                st.session_state["last_video"], st.session_state["last_cover"] = str(video), str(cover); st.success("Vídeo y portada terminados.")
        else:
            st.warning("El briefing y el paquete editorial ya están listos. El render se habilitará cuando incorporemos y validemos el banco de metraje real de esta idea.")

with tab_niches:
    st.subheader("Identidad del nicho"); st.json(active_niche.__dict__)
    with st.expander("Crear otro nicho"):
        with st.form("new-niche"):
            name = st.text_input("Nombre"); promise = st.text_input("Promesa editorial"); audience = st.text_input("Audiencia"); tone = st.text_input("Tono")
            if st.form_submit_button("Guardar nicho"):
                add_niche(LIBRARY, Niche(slugify(name), name, promise, audience, tone, "#FFD447", "#07111B", "Vídeo real prioritario.", "Gancho específico en los primeros 2 segundos.", ["¿Tú qué piensas? ↓"])); st.success("Nicho creado. Recarga para seleccionarlo.")

with tab_outputs:
    st.subheader("Entregables")
    projects = list(list_projects(LIBRARY))
    if not projects: st.caption("Todavía no hay proyectos.")
    for project in projects[:12]:
        record = json.loads((project / "project.json").read_text(encoding="utf-8"))
        with st.expander(record["idea"]["title"], expanded=project == projects[0]):
            pub = record["publication"]; st.caption(project.name); st.write(f"**Título:** {pub['title']}"); st.write(pub["description"]); st.code(" ".join(pub["hashtags"]), language=None)
            video, cover, publication = project / "video-final.mp4", project / "portada-9x16.jpg", project / "publicacion.txt"
            if video.exists(): st.video(str(video)); st.download_button("Descargar MP4", video.read_bytes(), video.name, "video/mp4", key=f"video-{project.name}")
            if cover.exists(): st.image(str(cover), width=230); st.download_button("Descargar portada", cover.read_bytes(), cover.name, "image/jpeg", key=f"cover-{project.name}")
            st.download_button("Descargar textos", publication.read_bytes(), publication.name, "text/plain", key=f"text-{project.name}")

st.caption("AutoShorts Studio funciona en local. Los proveedores de pago permanecen desactivados hasta que los autorices y configures.")
