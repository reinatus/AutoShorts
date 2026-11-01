from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .free_media import MediaCandidate, download, search_commons
from .production import build_storyboard, save_media_manifest, set_project_status, validate_media_records
from .studio import Niche, VideoIdea, create_cover, create_project, render_uploaded_short


SUBJECT_TERMS: dict[str, tuple[str, ...]] = {
    "octopus-neurons": ("octopus", "tentacles", "suckers"),
    "crow-faces": ("crow", "raven", "corvus"),
    "axolotl-regeneration": ("axolotl", "ambystoma mexicanum"),
    "wood-frog-freeze": ("wood frog", "rana sylvatica"),
    "dolphin-half-sleep": ("dolphin", "dolphins swimming"),
    "cuttlefish-disguise": ("cuttlefish", "sepia underwater"),
    "mantis-shrimp-punch": ("mantis shrimp", "stomatopoda"),
    "tardigrade-limits": ("tardigrade", "water bear microscopy"),
    "wombat-cubes": ("wombat", "vombatus"),
    "immortal-jellyfish": ("turritopsis", "jellyfish underwater"),
    "electric-eel-hunt": ("electric eel", "electrophorus"),
    "orca-culture": ("orca", "killer whale pod"),
    "roman-concrete": ("roman concrete", "roman ruins masonry"),
    "molasses-flood": ("great molasses flood", "boston north end archive"),
    "tyrian-purple": ("tyrian purple", "murex snail", "purple textile"),
    "dancing-plague": ("dancing plague", "strasbourg historic"),
    "blood-falls": ("blood falls antarctica", "taylor glacier"),
    "socotra-trees": ("socotra dragon blood tree", "dracaena cinnabari"),
    "danakil-colors": ("dallol danakil", "danakil depression"),
    "svalbard-burials": ("longyearbyen svalbard", "svalbard cemetery"),
    "petrichor": ("rain drops soil", "rain slow motion", "wet earth"),
    "metal-smell": ("hand coin macro", "metal coin close up"),
    "airplane-window-hole": ("airplane window", "aircraft window close up"),
    "onion-tears": ("cutting onion", "onion close up"),
    "solid-state-battery": ("solid state battery laboratory", "battery cell laboratory"),
    "fusion-reality": ("nuclear fusion laboratory", "tokamak", "laser fusion"),
    "soft-robots": ("soft robot", "soft robotics laboratory"),
    "photonic-chips": ("photonic chip", "silicon photonics laboratory"),
}

SPANISH_STOPWORDS = {
    "para", "como", "este", "esta", "esto", "unos", "unas", "desde", "donde",
    "puede", "porque", "sobre", "entre", "hacia", "tiene", "hacen", "solo", "propio",
    "propia", "animal", "video", "real", "primer", "plano", "detalle", "funciona",
}

IRRELEVANT_TITLE_TOKENS = {
    "trailer", "gameplay", "concert", "song", "album", "sheryl", "movie", "film", "animation",
}


def automatic_script(idea: VideoIdea, niche: Niche) -> str:
    middle_by_niche = {
        "mentes-salvajes": (
            "El comportamiento real no necesita exageraciones: la clave está en observar qué hace el animal y cómo lo consigue. "
            "Cada movimiento aporta una pista y permite separar el mecanismo comprobado del mito que suele circular en internet."
        ),
        "historia-oculta": (
            "El contexto cambia por completo la historia. Conviene separar los documentos y las pruebas de las versiones repetidas con el tiempo. "
            "Lo sorprendente no es la leyenda, sino lo que sí puede sostenerse cuando se revisan los hechos."
        ),
        "lugares-limite": (
            "La ubicación y las condiciones del entorno explican lo que estamos viendo. La escala, el clima y la geología importan más que cualquier imagen espectacular. "
            "Por eso cada plano debe mostrar el lugar concreto y no un paisaje parecido."
        ),
        "ciencia-invisible": (
            "El efecto parece cotidiano, pero detrás hay un mecanismo preciso. Si seguimos el proceso paso a paso, la explicación deja de parecer magia. "
            "Lo importante es ver la causa, el cambio y el resultado en ese orden."
        ),
        "futuro-real": (
            "El avance es real, pero conviene distinguir una demostración de laboratorio de un producto listo para todo el mundo. "
            "La pregunta útil no es si suena futurista, sino qué puede hacer hoy y qué obstáculo todavía falta resolver."
        ),
    }
    middle = middle_by_niche.get(
        niche.slug,
        "La explicación se entiende mejor cuando cada plano acompaña una idea concreta y evita rellenar el vídeo con imágenes genéricas.",
    )
    return " ".join(
        part.strip()
        for part in (
            idea.hook,
            f"La explicación real es esta: {idea.angle}",
            middle,
            f"La pista visual está aquí: {idea.visual_hook}",
            "Ahora que conoces el mecanismo, vuelve a mirar el primer plano. ¿Qué detalle te parece más sorprendente?",
        )
        if part.strip()
    )


def subject_terms(idea: VideoIdea) -> tuple[str, ...]:
    if idea.slug in SUBJECT_TERMS:
        return SUBJECT_TERMS[idea.slug]
    words = re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{4,}", f"{idea.title} {idea.visual_hook}".lower())
    useful = tuple(dict.fromkeys(word for word in words if word not in SPANISH_STOPWORDS))
    return useful[:3] or (idea.slug.replace("-", " "),)


def media_queries(idea: VideoIdea) -> list[str]:
    terms = subject_terms(idea)
    variants = ("close up video", "documentary video", "video", "webm")
    return list(dict.fromkeys(f"{term} {variant}" for term in terms for variant in variants))


def _candidate_matches(candidate: MediaCandidate, terms: tuple[str, ...]) -> bool:
    title = candidate.title.lower().replace("_", " ")
    if any(token in title for token in IRRELEVANT_TITLE_TOKENS):
        return False
    needles = {token for term in terms for token in re.findall(r"[a-z0-9]{4,}", term.lower())}
    resolution_ok = not candidate.width or (
        max(candidate.width, candidate.height) >= 720 and min(candidate.width, candidate.height) >= 360
    )
    return candidate.is_video and resolution_ok and bool(needles.intersection(re.findall(r"[a-z0-9]{4,}", title)))


def _record(path: Path, candidate: MediaCandidate, relevance: str) -> dict:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return {
        "filename": path.name,
        "size_bytes": path.stat().st_size,
        "sha256": digest.hexdigest(),
        "source": candidate.page_url or candidate.url,
        "license": candidate.license_name,
        "license_url": candidate.license_url,
        "artist": candidate.artist,
        "relevance": relevance,
        "download_url": candidate.url,
        "automatic_selection": True,
    }


def acquire_automatic_clips(project: Path, idea: VideoIdea, desired: int = 5) -> tuple[list[Path], list[dict]]:
    media = project / "media"
    media.mkdir(parents=True, exist_ok=True)
    terms = subject_terms(idea)
    selected: list[MediaCandidate] = []
    seen_urls: set[str] = set()

    for query in media_queries(idea):
        for candidate in search_commons(query, limit=50):
            if candidate.url in seen_urls or not _candidate_matches(candidate, terms):
                continue
            seen_urls.add(candidate.url)
            selected.append(candidate)
            break
        if len(selected) >= desired:
            break

    if len(selected) < 3:
        raise RuntimeError(
            "No se encontraron tres vídeos libres suficientemente relacionados con esta idea. "
            "La producción se ha detenido para no rellenarla con planos genéricos."
        )

    paths: list[Path] = []
    records: list[dict] = []
    errors: list[str] = []
    for index, candidate in enumerate(selected, 1):
        try:
            path = Path(download(candidate, str(media), f"{index:02d}-automatico", max_bytes=300 * 1024 * 1024))
        except Exception as error:
            errors.append(f"{candidate.title}: {error}")
            continue
        paths.append(path)
        records.append(_record(path, candidate, f"Plano automático sobre {terms[min(index - 1, len(terms) - 1)]}: {candidate.title}"))

    if len(paths) < 3:
        raise RuntimeError(
            "Solo se pudieron descargar " + str(len(paths)) + " clips válidos. "
            "La producción se detuvo antes del montaje. " + " | ".join(errors[:2])
        )
    return paths, validate_media_records(records)


def produce_automatic_short(
    repo_root: Path,
    library: Path,
    idea: VideoIdea,
    niche: Niche,
    cta_index: int = 0,
) -> tuple[Path, Path, Path]:
    script = automatic_script(idea, niche)
    project = create_project(library, idea, niche, script, cta_index)
    record_path = project / "project.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record["budget"] = {"cap_usd": 0.50, "target_usd": 0.40, "estimated_usd": 0.0, "actual_usd": 0.0, "mode": "free_local"}
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        set_project_status(project, "searching_free_media")
        clips, records = acquire_automatic_clips(project, idea)
        storyboard = build_storyboard(script, idea.visual_hook, records)
        save_media_manifest(project, records, storyboard)
        set_project_status(project, "rendering")
        video = render_uploaded_short(repo_root, project, clips, script, niche.cta_variants[cta_index])
        cover = create_cover(repo_root, video, project / "portada-9x16.jpg")
    except Exception as error:
        set_project_status(project, "failed", str(error))
        raise
    return project, video, cover

