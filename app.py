from __future__ import annotations

import html
import json
from pathlib import Path

import streamlit as st

from autoshorts.studio import (
    Niche,
    VideoIdea,
    add_idea,
    add_niche,
    create_cover,
    create_project,
    ensure_library,
    list_projects,
    render_octopus,
    slugify,
)


ROOT = Path(__file__).resolve().parent
LIBRARY = ROOT / "studio_data"
niches, ideas = ensure_library(LIBRARY)
niche_by_slug = {item.slug: item for item in niches}

st.set_page_config(page_title="AutoShorts Studio", page_icon="⚡", layout="wide")
st.markdown(
    """
<style>
:root{--ink:#F6F8FB;--muted:#91A1AF;--line:#243442;--panel:#0C1822;--yellow:#FFD447}
.stApp{background:radial-gradient(circle at 80% -20%,#183147 0,transparent 34%),#061019;color:var(--ink)}
[data-testid="stSidebar"]{background:#08141E;border-right:1px solid var(--line)}
[data-testid="stSidebar"] .block-container{padding-top:1.5rem}
.block-container{padding-top:2rem;max-width:1500px}
.brand{font-size:.76rem;letter-spacing:.18em;color:#8394A2;font-weight:800}.brand strong{color:#FFD447}
.hero{position:relative;overflow:hidden;padding:2rem 2.2rem;border:1px solid #2C3E4D;border-radius:24px;background:linear-gradient(125deg,#0D1F2D 0%,#0B1721 60%,#132735 100%);margin-bottom:1.1rem;box-shadow:0 22px 70px #0005}
.hero:after{content:"";position:absolute;width:260px;height:260px;border-radius:50%;right:-90px;top:-120px;background:var(--hero-accent,#FFD447);filter:blur(70px);opacity:.18}
.eyebrow{color:var(--hero-accent,#FFD447);font-weight:900;letter-spacing:.15em;font-size:.74rem}
.hero h1{margin:.35rem 0 .45rem;font-size:clamp(2rem,4vw,3.4rem);line-height:1.02;max-width:820px}.hero p{color:#B8C4CD;font-size:1.04rem;margin:0;max-width:820px}
.status{display:inline-flex;align-items:center;gap:.45rem;margin-top:1rem;color:#DCE5EB;font-size:.82rem}.dot{width:8px;height:8px;border-radius:50%;background:#55D68A;box-shadow:0 0 14px #55D68A}
.niche-card{min-height:205px;padding:1.15rem 1.25rem;border-radius:18px;background:linear-gradient(145deg,#0E1B26,#09131C);border:1px solid #263746;border-top:4px solid var(--accent);margin-bottom:.55rem}
.niche-kicker{color:var(--accent);font-weight:900;font-size:.7rem;letter-spacing:.13em}.niche-card h3{font-size:1.32rem;margin:.45rem 0}.niche-card p{color:#A9B6C0;min-height:48px}.niche-meta{color:#6F8291;font-size:.78rem;border-top:1px solid #20303C;padding-top:.7rem;margin-top:.7rem}
.idea-head{display:flex;align-items:center;gap:.6rem;flex-wrap:wrap}.score{display:inline-block;background:#FFD447;color:#101820;border-radius:999px;padding:.16rem .56rem;font-weight:900;font-size:.78rem}.niche-pill{display:inline-block;border:1px solid var(--accent);color:var(--accent);border-radius:999px;padding:.14rem .52rem;font-weight:700;font-size:.72rem}
div[data-testid="stMetric"]{background:linear-gradient(145deg,#0D1B26,#0A151E);border:1px solid #263746;padding:1rem 1.1rem;border-radius:16px}
div[data-testid="stMetricValue"]{color:#F8FAFC}
[data-baseweb="tab-list"]{gap:.4rem;border-bottom:1px solid #21313E}[data-baseweb="tab"]{color:#A9B6C0;background:#0A151E;border-radius:11px 11px 0 0;padding:.7rem 1.1rem}[aria-selected="true"][data-baseweb="tab"]{color:#FFD447;background:#101F2B}
.stButton>button{border-radius:11px;border-color:#314554}.stButton>button[kind="primary"]{background:#FFD447;color:#0A1117;border-color:#FFD447;font-weight:900}
small,.muted{color:#91A1AF}.section-copy{color:#9DABB6;margin-top:-.55rem;margin-bottom:1rem}
@media(max-width:700px){.hero{padding:1.4rem}.hero h1{font-size:2rem}.block-container{padding-left:1rem;padding-right:1rem}}
</style>
""",
    unsafe_allow_html=True,
)


def ideas_for(niche_slug: str | None) -> list[VideoIdea]:
    return [item for item in ideas if niche_slug is None or item.niche_slug == niche_slug]


def select_niche(slug: str) -> None:
    st.session_state["portfolio_filter"] = slug


def prepare_idea(idea: VideoIdea) -> None:
    st.session_state["selected_idea"] = idea.slug
    st.session_state["portfolio_filter"] = idea.niche_slug


with st.sidebar:
    st.markdown('<div class="brand"><strong>⚡ AUTOSHORTS</strong> / CONTROL ROOM</div>', unsafe_allow_html=True)
    st.markdown("### Cartera editorial")
    filter_options = ["all", *niche_by_slug]
    filter_names = {"all": "Todos los nichos", **{slug: niche.name for slug, niche in niche_by_slug.items()}}
    current_filter = st.session_state.get("portfolio_filter", "all")
    if current_filter not in filter_options:
        current_filter = "all"
    st.session_state.setdefault("portfolio_filter", current_filter)
    portfolio_filter = st.selectbox(
        "Vista",
        filter_options,
        format_func=filter_names.get,
        key="portfolio_filter",
    )
    scope_niche = niche_by_slug.get(portfolio_filter)
    if scope_niche:
        st.caption(scope_niche.promise)
        st.markdown(f'<div style="height:4px;border-radius:9px;background:{scope_niche.primary_color};margin:.8rem 0"></div>', unsafe_allow_html=True)
        st.button("← Ver toda la cartera", use_container_width=True, on_click=select_niche, args=("all",))
    else:
        st.caption("Cambia de temática sin salir del mismo flujo de trabajo.")
        st.markdown('<div style="height:4px;border-radius:9px;background:linear-gradient(90deg,#FFD447,#FF7A59,#31D7C8,#62A8FF,#B38CFF);margin:.8rem 0"></div>', unsafe_allow_html=True)
    st.divider()
    max_cost = st.number_input("Tope por Short (USD)", 0.0, 5.0, 0.50, 0.05)
    st.caption("Los servicios de pago están desactivados. Crear un proyecto no genera cargos.")
    st.divider()
    st.caption(f"{len(niches)} nichos · {len(ideas)} ideas · producción local")

scoped_ideas = ideas_for(scope_niche.slug if scope_niche else None)
hero_accent = scope_niche.primary_color if scope_niche else "#FFD447"
hero_title = scope_niche.name if scope_niche else "Tu cartera de canales, una sola fábrica"
hero_copy = scope_niche.promise if scope_niche else "Explora nichos, prioriza ideas y lleva cada vídeo desde el gancho hasta el paquete de publicación."
st.markdown(
    f'<div class="hero" style="--hero-accent:{hero_accent}"><div class="eyebrow">ESTUDIO MULTINICHO · LOCAL</div><h1>{html.escape(hero_title)}</h1><p>{html.escape(hero_copy)}</p><div class="status"><span class="dot"></span> Sin APIs de pago activas</div></div>',
    unsafe_allow_html=True,
)

tab_studio, tab_ideas, tab_create, tab_niches, tab_outputs = st.tabs(["Estudio", "Ideas", "Producción", "Nichos", "Entregables"])

with tab_studio:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Nichos activos", len(niches) if not scope_niche else 1)
    c2.metric("Ideas en cartera", len(scoped_ideas))
    c3.metric("Render directo", sum(item.renderer != "pending" for item in scoped_ideas))
    c4.metric("Tope USD", f"${max_cost:.2f}")
    st.subheader("Mapa de contenidos" if not scope_niche else "Dirección editorial")
    st.markdown('<p class="section-copy">Cada nicho mantiene su propia voz, color, gancho y política visual.</p>', unsafe_allow_html=True)
    visible_niches = niches if not scope_niche else [scope_niche]
    for row_start in range(0, len(visible_niches), 3):
        columns = st.columns(3)
        for column, niche in zip(columns, visible_niches[row_start:row_start + 3]):
            niche_ideas = ideas_for(niche.slug)
            top = max(niche_ideas, key=lambda item: item.viral_score) if niche_ideas else None
            with column:
                st.markdown(
                    f'<div class="niche-card" style="--accent:{niche.primary_color}"><div class="niche-kicker">CANAL · {len(niche_ideas)} IDEAS</div><h3>{html.escape(niche.name)}</h3><p>{html.escape(niche.promise)}</p><div class="niche-meta">Mejor oportunidad · {html.escape(top.title) if top else "Sin ideas todavía"}</div></div>',
                    unsafe_allow_html=True,
                )
                st.button("Abrir nicho →", key=f"open-{niche.slug}", use_container_width=True, on_click=select_niche, args=(niche.slug,))
    if scope_niche:
        left, right = st.columns(2)
        left.info(f"Gancho: {scope_niche.hook_formula}")
        right.info(f"Visuales: {scope_niche.visual_policy}")

with tab_ideas:
    st.subheader("Banco de ideas")
    st.markdown('<p class="section-copy">Compara oportunidades entre temáticas o trabaja solo dentro del nicho seleccionado.</p>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns([2, 1, 1])
    query = f1.text_input("Buscar", placeholder="historia, animales, tecnología…")
    niche_choices = ["all", *niche_by_slug]
    ideas_niche = f2.selectbox(
        "Nicho",
        niche_choices,
        index=niche_choices.index(scope_niche.slug) if scope_niche else 0,
        format_func=filter_names.get,
        key="ideas_niche_filter",
    )
    difficulty = f3.multiselect("Dificultad", ["baja", "media", "alta"], default=["baja", "media", "alta"])
    filtered = [
        item for item in ideas
        if (ideas_niche == "all" or item.niche_slug == ideas_niche)
        and item.visual_difficulty in difficulty
        and (not query or query.lower() in f"{item.title} {item.angle} {niche_by_slug[item.niche_slug].name}".lower())
    ]
    for idea in sorted(filtered, key=lambda item: item.viral_score, reverse=True):
        niche = niche_by_slug[idea.niche_slug]
        with st.container(border=True):
            col, action = st.columns([5, 1])
            col.markdown(
                f'<div class="idea-head" style="--accent:{niche.primary_color}"><span class="score">{idea.viral_score}/100</span><span class="niche-pill">{html.escape(niche.name)}</span><strong>{html.escape(idea.title)}</strong></div>',
                unsafe_allow_html=True,
            )
            col.caption(idea.angle)
            col.write(f"**Gancho:** {idea.hook}")
            col.write(f"**Primer plano:** {idea.visual_hook}")
            col.caption(f"Dificultad {idea.visual_difficulty} · coste previsto ${idea.estimated_cost_usd:.2f} · {idea.status}")
            action.button("Producir", key=f"use-{idea.slug}", use_container_width=True, on_click=prepare_idea, args=(idea,))
    with st.expander("Añadir una idea"):
        with st.form("new-idea"):
            idea_niche_slug = st.selectbox("Nicho", list(niche_by_slug), format_func=lambda slug: niche_by_slug[slug].name)
            title = st.text_input("Título de trabajo")
            angle = st.text_area("Ángulo")
            hook = st.text_input("Gancho")
            visual = st.text_input("Primer plano imprescindible")
            score = st.slider("Puntuación editorial", 1, 100, 75)
            if st.form_submit_button("Guardar idea"):
                add_idea(LIBRARY, VideoIdea(slugify(title), idea_niche_slug, title, angle, hook, visual, score, "media", 0.0))
                st.success("Idea guardada.")
                st.rerun()

with tab_create:
    st.subheader("Producción")
    st.markdown('<p class="section-copy">Elige cualquier idea: el estudio aplica automáticamente la identidad correcta.</p>', unsafe_allow_html=True)
    production_pool = scoped_ideas or ideas
    selected_slug = st.session_state.get("selected_idea", production_pool[0].slug)
    if selected_slug not in {item.slug for item in production_pool}:
        selected_slug = production_pool[0].slug
    choices = {item.slug: f"{niche_by_slug[item.niche_slug].name}  ·  {item.title}" for item in production_pool}
    selected_slug = st.selectbox("Idea", list(choices), index=list(choices).index(selected_slug), format_func=choices.get)
    idea = next(item for item in production_pool if item.slug == selected_slug)
    production_niche = niche_by_slug[idea.niche_slug]
    st.markdown(
        f'<div class="niche-card" style="--accent:{production_niche.primary_color};min-height:auto"><div class="niche-kicker">IDENTIDAD APLICADA</div><h3>{html.escape(production_niche.name)}</h3><p style="min-height:auto">{html.escape(production_niche.tone)}</p></div>',
        unsafe_allow_html=True,
    )
    default_script = (ROOT / "real_media" / "octopus" / "narracion.txt").read_text(encoding="utf-8") if idea.renderer == "octopus" else f"{idea.hook}\n\n{idea.angle}\n\n[Cierra con una pregunta que invite a comentar.]"
    script = st.text_area("Guion", default_script, height=220)
    cta_index = st.selectbox("Acción final", range(len(production_niche.cta_variants)), format_func=lambda i: production_niche.cta_variants[i])
    col1, col2, col3 = st.columns(3)
    col1.write(f"**Plano de apertura**  \n{idea.visual_hook}")
    col2.write(f"**Política visual**  \n{production_niche.visual_policy}")
    col3.metric("Coste previsto", f"${idea.estimated_cost_usd:.2f}", f"tope ${max_cost:.2f}")
    blocked = idea.estimated_cost_usd > max_cost
    if blocked:
        st.error("Esta idea supera el presupuesto y no puede ejecutarse.")
    if st.button("Crear proyecto", type="primary", use_container_width=True, disabled=blocked):
        project = create_project(LIBRARY, idea, production_niche, script, cta_index)
        st.session_state["current_project"] = str(project)
        st.session_state["current_idea"] = idea.slug
        st.success("Proyecto, briefing y paquete de publicación creados.")
    project_value = st.session_state.get("current_project")
    if project_value and st.session_state.get("current_idea") == idea.slug:
        project = Path(project_value)
        st.caption(f"Proyecto: {project.name}")
        if idea.renderer == "octopus":
            if st.button("Renderizar vídeo final", use_container_width=True):
                with st.spinner("Renderizando localmente. No cierres esta ventana…"):
                    video = render_octopus(ROOT, project, cta_index)
                    cover = create_cover(ROOT, video, project / "portada-9x16.jpg")
                st.session_state["last_video"], st.session_state["last_cover"] = str(video), str(cover)
                st.success("Vídeo y portada terminados.")
        else:
            st.warning("Briefing listo. El render se habilitará cuando exista un banco de metraje real validado para esta idea.")

with tab_niches:
    st.subheader("Identidades editoriales")
    st.markdown('<p class="section-copy">Cinco canales posibles, cada uno con reglas visuales y voz propias.</p>', unsafe_allow_html=True)
    for niche in niches:
        with st.expander(f"{niche.name}  ·  {len(ideas_for(niche.slug))} ideas", expanded=scope_niche is not None and niche.slug == scope_niche.slug):
            left, right = st.columns(2)
            left.write(f"**Promesa:** {niche.promise}")
            left.write(f"**Audiencia:** {niche.audience}")
            right.write(f"**Tono:** {niche.tone}")
            right.write(f"**Gancho:** {niche.hook_formula}")
            st.caption(niche.visual_policy)
    with st.expander("Crear otro nicho"):
        with st.form("new-niche"):
            name = st.text_input("Nombre")
            promise = st.text_input("Promesa editorial")
            audience = st.text_input("Audiencia")
            tone = st.text_input("Tono")
            color = st.color_picker("Color de identidad", "#FFD447")
            if st.form_submit_button("Guardar nicho"):
                add_niche(LIBRARY, Niche(slugify(name), name, promise, audience, tone, color, "#07111B", "Vídeo real prioritario.", "Gancho específico en los primeros 2 segundos.", ["¿Tú qué piensas? ↓"]))
                st.success("Nicho creado.")
                st.rerun()

with tab_outputs:
    st.subheader("Entregables")
    st.markdown('<p class="section-copy">Vídeo, portada y textos reunidos por proyecto, sin mezclar identidades.</p>', unsafe_allow_html=True)
    projects = list(list_projects(LIBRARY))
    if not projects:
        st.caption("Todavía no hay proyectos.")
    for project in projects[:12]:
        record = json.loads((project / "project.json").read_text(encoding="utf-8"))
        project_niche = record.get("niche", {})
        with st.expander(f"{project_niche.get('name', 'Sin nicho')}  ·  {record['idea']['title']}", expanded=project == projects[0]):
            pub = record["publication"]
            st.caption(project.name)
            st.write(f"**Título:** {pub['title']}")
            st.write(pub["description"])
            st.code(" ".join(pub["hashtags"]), language=None)
            video, cover, publication = project / "video-final.mp4", project / "portada-9x16.jpg", project / "publicacion.txt"
            if video.exists():
                st.video(str(video))
                st.download_button("Descargar MP4", video.read_bytes(), video.name, "video/mp4", key=f"video-{project.name}")
            if cover.exists():
                st.image(str(cover), width=230)
                st.download_button("Descargar portada", cover.read_bytes(), cover.name, "image/jpeg", key=f"cover-{project.name}")
            st.download_button("Descargar textos", publication.read_bytes(), publication.name, "text/plain", key=f"text-{project.name}")

st.caption("AutoShorts Studio funciona en local. Crear ideas y proyectos no consume uso de Codex ni activa proveedores de pago.")
