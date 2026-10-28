from __future__ import annotations

import html
import json
from pathlib import Path

import streamlit as st

from autoshorts.production import (
    MediaValidationError,
    build_storyboard,
    project_archive_bytes,
    save_media_manifest,
    set_project_status,
    sha256_bytes,
    validate_media_records,
)

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
    render_uploaded_short,
    slugify,
)


ROOT = Path(__file__).resolve().parent
LIBRARY = ROOT / "studio_data"
niches, ideas = ensure_library(LIBRARY)
niche_by_slug = {item.slug: item for item in niches}


def project_ideas(slug: str) -> list[VideoIdea]:
    return sorted((item for item in ideas if item.niche_slug == slug), key=lambda item: item.viral_score, reverse=True)


def open_project(slug: str) -> None:
    st.session_state["project_slug"] = slug
    st.session_state["project_view"] = "videos"


def open_portfolio() -> None:
    st.session_state["project_slug"] = "portfolio"


def set_view(view: str) -> None:
    st.session_state["project_view"] = view


def open_generator(idea: VideoIdea) -> None:
    st.session_state["project_slug"] = idea.niche_slug
    st.session_state["selected_idea"] = idea.slug
    st.session_state["project_view"] = "generate"


st.set_page_config(page_title="AutoShorts", page_icon="▶", layout="wide", initial_sidebar_state="collapsed")
st.markdown(
    """
<style>
:root{--bg:#0B0D10;--surface:#12151A;--surface2:#171B21;--line:#282E37;--text:#F5F6F7;--muted:#939BA7;--accent:#F4E35D}
.stApp{background:var(--bg);color:var(--text)}
.block-container{max-width:1480px;padding-top:1.55rem;padding-bottom:4rem}
[data-testid="stSidebar"]{background:#0F1216;border-right:1px solid #242932}
[data-testid="stSidebar"] .block-container{padding-top:1.35rem}
.logo{font-size:1.08rem;font-weight:950;letter-spacing:-.03em}.logo b{display:inline-grid;place-items:center;width:27px;height:27px;border-radius:8px;background:#F4E35D;color:#111;margin-right:.45rem}.sidebar-label{font-size:.67rem;font-weight:850;letter-spacing:.16em;color:#737C88;margin:1.6rem 0 .6rem}
.project-head{display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;border-bottom:1px solid var(--line);padding:.4rem 0 1.35rem;margin-bottom:1.1rem}.breadcrumb{font-size:.72rem;color:#7F8995;letter-spacing:.1em;text-transform:uppercase;font-weight:800}.project-head h1{font-size:clamp(2rem,4vw,3.15rem);letter-spacing:-.055em;margin:.35rem 0 .4rem;line-height:1}.project-head p{color:#A5ADB7;margin:0;max-width:760px}.project-mark{width:64px;height:64px;border-radius:18px;background:var(--project-color);box-shadow:0 0 50px color-mix(in srgb,var(--project-color) 30%,transparent)}
.nav-strip{display:flex;gap:.5rem;margin-bottom:1.5rem}.nav-label{font-size:.78rem;font-weight:800;color:#98A1AC}
.section-title{font-size:1.55rem;letter-spacing:-.035em;margin:0}.section-sub{color:#8F98A3;margin:.35rem 0 1.2rem}
.video-card{position:relative;min-height:285px;border:1px solid var(--line);border-radius:16px;background:linear-gradient(145deg,#15191F,#111419);padding:1.15rem 1.2rem;margin-bottom:.65rem;overflow:hidden}.video-card:before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--project-color)}.video-top{display:flex;align-items:center;justify-content:space-between;gap:.5rem}.number{font:800 .72rem/1 monospace;color:#707A86}.score{font-size:.72rem;font-weight:850;background:#20262D;border:1px solid #343C46;padding:.28rem .5rem;border-radius:999px}.video-card h3{font-size:1.22rem;letter-spacing:-.025em;margin:.9rem 0 .55rem}.hook{color:#F3F4F5;font-size:.95rem;line-height:1.42;margin:.6rem 0}.visual{font-size:.82rem;color:#89939F;border-top:1px solid #252B33;margin-top:.8rem;padding-top:.75rem}.meta{display:flex;gap:.5rem;flex-wrap:wrap;margin-top:.8rem}.tag{font-size:.67rem;text-transform:uppercase;letter-spacing:.07em;color:#929BA6;border:1px solid #303741;border-radius:5px;padding:.23rem .38rem}
.brief{border:1px solid var(--line);border-left:4px solid var(--project-color);background:#12161B;border-radius:12px;padding:1rem 1.15rem;margin:.7rem 0 1rem}.brief-kicker{font-size:.67rem;letter-spacing:.12em;font-weight:900;color:var(--project-color)}.brief h3{margin:.35rem 0}.brief p{color:#9EA7B1;margin:.2rem 0}
.portfolio-card{min-height:220px;border:1px solid var(--line);border-top:4px solid var(--project-color);border-radius:17px;background:#12161B;padding:1.2rem;margin-bottom:.6rem}.portfolio-card small{color:var(--project-color);font-weight:900;letter-spacing:.12em}.portfolio-card h3{font-size:1.35rem;margin:.55rem 0}.portfolio-card p{color:#929CA7;min-height:52px}.portfolio-meta{font-size:.78rem;color:#737D89;border-top:1px solid #262C34;padding-top:.7rem}
.status-ready{color:#6DE2A3}.status-blocked{color:#FFB96A}.empty{border:1px dashed #303741;border-radius:14px;padding:2rem;text-align:center;color:#89939F}
div[data-testid="stMetric"]{background:#12161B;border:1px solid #292F38;border-radius:14px;padding:.9rem 1rem}div[data-testid="stMetricValue"]{font-size:1.75rem}
.stButton>button{border-radius:9px;border:1px solid #343B45;background:#171B21;color:#E9EBEE;font-weight:750}.stButton>button:hover{border-color:#F4E35D;color:#F4E35D}.stButton>button[kind="primary"]{background:#F4E35D;color:#111;border-color:#F4E35D;font-weight:900}
[data-testid="stSidebar"] .stButton>button{justify-content:flex-start;background:transparent;border-color:transparent;color:#A7AFB9;padding-left:.35rem}[data-testid="stSidebar"] .stButton>button:hover{background:#191E24;border-color:#2B323B;color:#FFF}
.danger-note{font-size:.78rem;color:#858E99}.stTextArea textarea,.stTextInput input{background:#11151A;border-color:#303741}
@media(max-width:760px){.project-mark{display:none}.project-head h1{font-size:2.05rem}.block-container{padding-left:1rem;padding-right:1rem}.video-card{min-height:auto}}
</style>
""",
    unsafe_allow_html=True,
)

st.session_state.setdefault("project_slug", niches[0].slug)
st.session_state.setdefault("project_view", "videos")
selected_project = st.session_state["project_slug"]

with st.sidebar:
    st.markdown('<div class="logo"><b>▶</b> AutoShorts</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-label">PROYECTOS</div>', unsafe_allow_html=True)
    st.button("▦  Todos los proyectos", use_container_width=True, on_click=open_portfolio)
    for niche in niches:
        marker = "●" if niche.slug == selected_project else "○"
        st.button(f"{marker}  {niche.name}", key=f"side-{niche.slug}", use_container_width=True, on_click=open_project, args=(niche.slug,))
    st.divider()
    with st.expander("＋ Nuevo proyecto"):
        with st.form("new-project"):
            name = st.text_input("Nombre del proyecto")
            promise = st.text_input("Qué promete al espectador")
            audience = st.text_input("Audiencia")
            tone = st.text_input("Tono")
            color = st.color_picker("Color", "#F4E35D")
            if st.form_submit_button("Crear proyecto"):
                new_slug = slugify(name)
                add_niche(LIBRARY, Niche(new_slug, name, promise, audience, tone, color, "#0B0D10", "Vídeo real y específico para cada frase.", "Gancho visual y verbal en los dos primeros segundos.", ["¿Tú qué piensas? Déjalo en comentarios ↓"]))
                st.session_state["project_slug"] = new_slug
                st.session_state["project_view"] = "videos"
                st.rerun()
    st.markdown('<div class="sidebar-label">CONTROL</div>', unsafe_allow_html=True)
    max_cost = st.number_input("Tope por vídeo (USD)", 0.0, 5.0, 0.50, 0.05)
    st.markdown('<p class="danger-note">No se ejecutan proveedores de pago sin autorización.</p>', unsafe_allow_html=True)

if selected_project == "portfolio" or selected_project not in niche_by_slug:
    st.markdown('<div class="breadcrumb">AutoShorts / Proyectos</div>', unsafe_allow_html=True)
    st.title("Tus proyectos")
    st.markdown('<p class="section-sub">Cada proyecto es un canal independiente con sus propias ideas, identidad, producción y entregables.</p>', unsafe_allow_html=True)
    for start in range(0, len(niches), 3):
        cols = st.columns(3)
        for col, niche in zip(cols, niches[start:start + 3]):
            niche_ideas = project_ideas(niche.slug)
            completed = sum(1 for folder in list_projects(LIBRARY) if json.loads((folder / "project.json").read_text(encoding="utf-8")).get("niche", {}).get("slug") == niche.slug)
            with col:
                st.markdown(
                    f'<div class="portfolio-card" style="--project-color:{niche.primary_color}"><small>PROYECTO</small><h3>{html.escape(niche.name)}</h3><p>{html.escape(niche.promise)}</p><div class="portfolio-meta">{len(niche_ideas)} ideas de vídeo · {completed} producciones</div></div>',
                    unsafe_allow_html=True,
                )
                st.button("Abrir panel", key=f"portfolio-{niche.slug}", use_container_width=True, on_click=open_project, args=(niche.slug,))
    st.stop()

niche = niche_by_slug[selected_project]
niche_ideas = project_ideas(niche.slug)
st.markdown(
    f'<div class="project-head" style="--project-color:{niche.primary_color}"><div><div class="breadcrumb">Proyectos / {html.escape(niche.name)}</div><h1>{html.escape(niche.name)}</h1><p>{html.escape(niche.promise)}</p></div><div class="project-mark"></div></div>',
    unsafe_allow_html=True,
)

views = [("overview", "Resumen"), ("videos", "Ideas de vídeos"), ("generate", "Generar vídeo"), ("outputs", "Entregables"), ("identity", "Identidad")]
nav_cols = st.columns(len(views))
for col, (view_key, view_label) in zip(nav_cols, views):
    col.button(view_label, key=f"nav-{view_key}", type="primary" if st.session_state["project_view"] == view_key else "secondary", use_container_width=True, on_click=set_view, args=(view_key,))

view = st.session_state["project_view"]

if view == "overview":
    project_folders = [folder for folder in list_projects(LIBRARY) if json.loads((folder / "project.json").read_text(encoding="utf-8")).get("niche", {}).get("slug") == niche.slug]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Ideas de vídeos", len(niche_ideas))
    m2.metric("Producciones", len(project_folders))
    m3.metric("Render directo", sum(item.renderer != "pending" for item in niche_ideas))
    m4.metric("Tope", f"${max_cost:.2f}")
    st.markdown("### Próximos vídeos")
    for idea in niche_ideas[:3]:
        left, right = st.columns([5, 1])
        left.write(f"**{idea.title}**  \n{idea.hook}")
        right.button("Generar", key=f"quick-{idea.slug}", use_container_width=True, on_click=open_generator, args=(idea,))
        st.divider()

elif view == "videos":
    st.markdown('<h2 class="section-title">Ideas de vídeos</h2>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-sub">{len(niche_ideas)} vídeos concretos para {html.escape(niche.name)}. Pulsa Generar para llevar una idea directamente a producción.</p>', unsafe_allow_html=True)
    search_col, difficulty_col = st.columns([3, 1])
    query = search_col.text_input("Buscar vídeo", placeholder="Busca por título, gancho o tema…", key=f"search-{niche.slug}")
    difficulty = difficulty_col.selectbox("Dificultad", ["todas", "baja", "media", "alta"], key=f"difficulty-{niche.slug}")
    filtered = [item for item in niche_ideas if (difficulty == "todas" or item.visual_difficulty == difficulty) and (not query or query.lower() in f"{item.title} {item.hook} {item.angle}".lower())]
    for start in range(0, len(filtered), 2):
        cols = st.columns(2)
        for col, idea in zip(cols, filtered[start:start + 2]):
            render_state = "Render completo disponible" if idea.renderer != "pending" else "Requiere metraje real"
            with col:
                st.markdown(
                    f'<div class="video-card" style="--project-color:{niche.primary_color}"><div class="video-top"><span class="number">VIDEO {niche_ideas.index(idea)+1:02d}</span><span class="score">{idea.viral_score}/100</span></div><h3>{html.escape(idea.title)}</h3><div class="hook">“{html.escape(idea.hook)}”</div><div class="visual"><b>APERTURA:</b> {html.escape(idea.visual_hook)}</div><div class="meta"><span class="tag">{idea.visual_difficulty}</span><span class="tag">${idea.estimated_cost_usd:.2f}</span><span class="tag">{render_state}</span></div></div>',
                    unsafe_allow_html=True,
                )
                st.button("Generar este vídeo →", key=f"generate-{idea.slug}", type="primary", use_container_width=True, on_click=open_generator, args=(idea,))
    if not filtered:
        st.markdown('<div class="empty">No hay vídeos que coincidan con los filtros.</div>', unsafe_allow_html=True)
    with st.expander("＋ Añadir idea de vídeo"):
        with st.form(f"new-video-{niche.slug}"):
            title = st.text_input("Título")
            hook = st.text_input("Gancho de los primeros 2 segundos")
            angle = st.text_area("Qué cuenta y por qué interesa")
            visual = st.text_input("Plano real imprescindible al comienzo")
            score = st.slider("Potencial editorial", 1, 100, 75)
            if st.form_submit_button("Guardar idea de vídeo"):
                add_idea(LIBRARY, VideoIdea(slugify(title), niche.slug, title, angle, hook, visual, score, "media", 0.0))
                st.success("Idea añadida al proyecto.")
                st.rerun()

elif view == "generate":
    st.markdown('<h2 class="section-title">Generar vídeo</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Configura y ejecuta la producción sin salir del panel del proyecto.</p>', unsafe_allow_html=True)
    if not niche_ideas:
        st.markdown('<div class="empty">Añade primero una idea de vídeo desde este proyecto.</div>', unsafe_allow_html=True)
        st.stop()
    selected_slug = st.session_state.get("selected_idea", niche_ideas[0].slug)
    if selected_slug not in {item.slug for item in niche_ideas}:
        selected_slug = niche_ideas[0].slug
    idea_labels = {item.slug: item.title for item in niche_ideas}
    selected_slug = st.selectbox("Idea de vídeo", list(idea_labels), index=list(idea_labels).index(selected_slug), format_func=idea_labels.get, key=f"generator-picker-{niche.slug}")
    idea = next(item for item in niche_ideas if item.slug == selected_slug)
    st.markdown(
        f'<div class="brief" style="--project-color:{niche.primary_color}"><div class="brief-kicker">BRIEF DE PRODUCCIÓN</div><h3>{html.escape(idea.hook)}</h3><p><b>Primer plano:</b> {html.escape(idea.visual_hook)}</p><p><b>Dirección:</b> {html.escape(idea.angle)}</p></div>',
        unsafe_allow_html=True,
    )
    default_script = (ROOT / "real_media" / "octopus" / "narracion.txt").read_text(encoding="utf-8") if idea.renderer == "octopus" else f"{idea.hook}\n\n{idea.angle}\n\n[Cierre potente seguido de una invitación breve a comentar.]"
    script = st.text_area("Guion", default_script, height=220, key=f"script-{idea.slug}")
    cta_index = st.selectbox("Cierre e interacción", range(len(niche.cta_variants)), format_func=lambda index: niche.cta_variants[index], key=f"cta-{niche.slug}")
    b1, b2, b3 = st.columns(3)
    b1.metric("Duración", "40 s")
    b2.metric("Coste previsto", f"${idea.estimated_cost_usd:.2f}")
    b3.metric("Límite", f"${max_cost:.2f}")
    blocked_budget = idea.estimated_cost_usd > max_cost
    if blocked_budget:
        st.error("Producción bloqueada: supera el límite configurado.")
    if idea.renderer == "octopus":
        st.success("Todo el metraje, la narración y la plantilla están validados. Este vídeo puede generarse completamente en local.")
        if st.button("▶  GENERAR VÍDEO FINAL", type="primary", use_container_width=True, disabled=blocked_budget):
            project = create_project(LIBRARY, idea, niche, script, cta_index)
            set_project_status(project, "rendering")
            try:
                with st.spinner("Generando vídeo y portada en local…"):
                    video = render_octopus(ROOT, project, cta_index)
                    cover = create_cover(ROOT, video, project / "portada-9x16.jpg")
            except Exception as error:
                set_project_status(project, "failed", str(error))
                st.error(f"El render se ha detenido sin perder el proyecto: {error}")
            else:
                st.session_state["last_project"] = str(project)
                st.success("Vídeo final, portada y paquete de publicación terminados.")
                st.video(str(video))
                st.download_button("Descargar vídeo", video.read_bytes(), video.name, "video/mp4")
                st.download_button("Descargar portada", cover.read_bytes(), cover.name, "image/jpeg")
    else:
        st.warning("Para evitar montajes genéricos, revisa cada clip y su función antes de renderizar.")
        uploaded = st.file_uploader(
            "Añade entre 3 y 12 clips reales aprobados",
            type=["mp4", "mov", "webm"],
            accept_multiple_files=True,
            key=f"clips-{idea.slug}",
        )
        draft_records = []
        for index, clip in enumerate(uploaded, 1):
            payload = clip.getvalue()
            with st.expander(f"Plano {index}: {Path(clip.name).name}", expanded=index <= 3):
                st.video(payload)
                source = st.text_input(
                    "Fuente o propietario",
                    value="Material propio / archivo local",
                    key=f"source-{idea.slug}-{index}",
                )
                license_name = st.selectbox(
                    "Licencia",
                    ["Material propio", "Dominio público", "CC BY", "CC BY-SA", "Licencia comercial", "Otra: revisar"],
                    key=f"license-{idea.slug}-{index}",
                )
                relevance = st.text_input(
                    "Qué muestra y qué frase acompaña",
                    placeholder="Ej.: primer plano real del animal moviendo los tentáculos",
                    key=f"relevance-{idea.slug}-{index}",
                )
            draft_records.append(
                {
                    "filename": Path(clip.name).name,
                    "size_bytes": len(payload),
                    "sha256": sha256_bytes(payload),
                    "source": source,
                    "license": license_name,
                    "relevance": relevance,
                }
            )

        validation_error = ""
        approved_records = []
        if uploaded:
            try:
                approved_records = validate_media_records(draft_records)
            except MediaValidationError as error:
                validation_error = str(error)
                st.error(validation_error)

        storyboard = build_storyboard(script, idea.visual_hook, approved_records)
        if storyboard:
            st.markdown("#### Storyboard previo")
            st.caption("Comprueba que cada plano corresponde con lo que se está contando. El primer plano debe sostener el gancho.")
            st.dataframe(
                [
                    {
                        "Escena": row["scene"],
                        "Tiempo": f'{row["start"]:.1f}–{row["end"]:.1f} s',
                        "Clip": row["clip"],
                        "Función visual": row["purpose"],
                        "Narración": row["narration"],
                    }
                    for row in storyboard
                ],
                use_container_width=True,
                hide_index=True,
            )

        rights_ok = st.checkbox(
            "Confirmo que las fuentes y licencias indicadas permiten utilizar estos clips.",
            key=f"rights-{idea.slug}",
        )
        storyboard_ok = st.checkbox(
            "He revisado el storyboard: ningún plano es genérico, repetido o ajeno a la narración.",
            key=f"storyboard-{idea.slug}",
        )
        ready = bool(approved_records) and not validation_error and rights_ok and storyboard_ok
        if uploaded:
            st.caption(f"{len(uploaded)} clips añadidos · máximo 300 MB por clip · máximo 1 GB en total.")

        if st.button(
            "▶  GENERAR VÍDEO CON ESTE STORYBOARD",
            type="primary",
            use_container_width=True,
            disabled=blocked_budget or not ready,
        ):
            project = create_project(LIBRARY, idea, niche, script, cta_index)
            media = project / "media"
            media.mkdir(exist_ok=True)
            clip_paths = []
            saved_records = []
            for index, (clip, record) in enumerate(zip(uploaded, approved_records), 1):
                clip_path = media / f"{index:02d}-{Path(clip.name).name}"
                clip_path.write_bytes(clip.getvalue())
                clip_paths.append(clip_path)
                saved_records.append({**record, "original_filename": record["filename"], "filename": clip_path.name})
            final_storyboard = build_storyboard(script, idea.visual_hook, saved_records)
            save_media_manifest(project, saved_records, final_storyboard)
            set_project_status(project, "rendering")
            try:
                with st.spinner("Generando narración, subtítulos, montaje y portada en local…"):
                    video = render_uploaded_short(ROOT, project, clip_paths, script, niche.cta_variants[cta_index])
                    cover = create_cover(ROOT, video, project / "portada-9x16.jpg")
            except Exception as error:
                set_project_status(project, "failed", str(error))
                st.error(f"El render se ha detenido sin perder el proyecto: {error}")
            else:
                st.session_state["last_project"] = str(project)
                st.success("Vídeo final, narración, subtítulos, cierre, portada y textos terminados.")
                st.video(str(video))
                st.download_button("Descargar vídeo", video.read_bytes(), video.name, "video/mp4", key=f"download-uploaded-{project.name}")
                st.download_button("Descargar portada", cover.read_bytes(), cover.name, "image/jpeg", key=f"download-cover-{project.name}")

elif view == "outputs":
    st.markdown('<h2 class="section-title">Entregables</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Solo aparecen los trabajos de este proyecto.</p>', unsafe_allow_html=True)
    folders = []
    for folder in list_projects(LIBRARY):
        record = json.loads((folder / "project.json").read_text(encoding="utf-8"))
        if record.get("niche", {}).get("slug") == niche.slug:
            folders.append((folder, record))
    if not folders:
        st.markdown('<div class="empty">Este proyecto todavía no tiene producciones.</div>', unsafe_allow_html=True)
    for folder, record in folders:
        with st.expander(record["idea"]["title"], expanded=folder == folders[0][0]):
            pub = record["publication"]
            status = record.get("status", "sin_estado")
            st.caption(f"{folder.name} · estado: {status}")
            if status == "failed":
                st.error(record.get("last_error", "El render anterior no terminó."))
            elif status == "rendering":
                st.warning("Este proyecto quedó marcado como renderizando. Puedes reintentarlo si el proceso ya no está activo.")
            st.write(f"**Título:** {pub['title']}")
            st.write(pub["description"])
            st.code(" ".join(pub["hashtags"]), language=None)
            video, cover, publication = folder / "video-final.mp4", folder / "portada-9x16.jpg", folder / "publicacion.txt"
            manifest = folder / "media-manifest.json"
            if manifest.exists():
                with st.expander("Fuentes, licencias y storyboard"):
                    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
                    for item in manifest_data.get("clips", []):
                        st.write(f"**{item['filename']}** · {item['license']}  \\n{item['source']} — {item['relevance']}")
                    st.download_button(
                        "Descargar manifiesto",
                        manifest.read_bytes(),
                        manifest.name,
                        "application/json",
                        key=f"manifest-{folder.name}",
                    )
            if status in {"failed", "rendering"}:
                if st.button("Reintentar render", key=f"retry-{folder.name}", use_container_width=True):
                    set_project_status(folder, "rendering")
                    try:
                        if record.get("idea", {}).get("renderer") == "octopus":
                            cta_value = pub.get("cta", "")
                            retry_cta = niche.cta_variants.index(cta_value) if cta_value in niche.cta_variants else 0
                            retry_video = render_octopus(ROOT, folder, retry_cta)
                        else:
                            retry_clips = sorted((folder / "media").glob("*"))
                            retry_video = render_uploaded_short(ROOT, folder, retry_clips, record.get("script", ""), pub.get("cta", ""))
                        create_cover(ROOT, retry_video, cover)
                    except Exception as error:
                        set_project_status(folder, "failed", str(error))
                        st.error(f"No se pudo completar el reintento: {error}")
                    else:
                        st.success("Render recuperado correctamente.")
                        st.rerun()
            if video.exists():
                st.video(str(video))
                st.download_button("Descargar MP4", video.read_bytes(), video.name, "video/mp4", key=f"video-{folder.name}")
            if cover.exists():
                st.image(str(cover), width=220)
                st.download_button("Descargar portada", cover.read_bytes(), cover.name, "image/jpeg", key=f"cover-{folder.name}")
            st.download_button("Descargar título, descripción y hashtags", publication.read_bytes(), publication.name, "text/plain", key=f"text-{folder.name}")
            st.download_button(
                "Descargar paquete completo ZIP",
                project_archive_bytes(folder),
                f"{folder.name}-entregables.zip",
                "application/zip",
                key=f"package-{folder.name}",
                use_container_width=True,
            )

elif view == "identity":
    st.markdown('<h2 class="section-title">Identidad del proyecto</h2>', unsafe_allow_html=True)
    left, right = st.columns(2)
    left.markdown(f"**Promesa**  \n{niche.promise}")
    left.markdown(f"**Audiencia**  \n{niche.audience}")
    left.markdown(f"**Tono**  \n{niche.tone}")
    right.markdown(f"**Fórmula de gancho**  \n{niche.hook_formula}")
    right.markdown(f"**Política visual**  \n{niche.visual_policy}")
    right.color_picker("Color del proyecto", niche.primary_color, disabled=True)

st.caption("AutoShorts funciona en local. El panel nunca activa proveedores de pago sin autorización.")
