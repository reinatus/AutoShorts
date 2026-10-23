from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


@dataclass
class Niche:
    slug: str
    name: str
    promise: str
    audience: str
    tone: str
    primary_color: str
    background_color: str
    visual_policy: str
    hook_formula: str
    cta_variants: list[str] = field(default_factory=list)


@dataclass
class VideoIdea:
    slug: str
    niche_slug: str
    title: str
    angle: str
    hook: str
    visual_hook: str
    viral_score: int
    visual_difficulty: str
    estimated_cost_usd: float
    status: str = "idea"
    renderer: str = "pending"
    evidence_notes: str = "Requiere contraste científico antes de publicar."


WILDLIFE_NICHE = Niche(
    "mentes-salvajes", "Mentes Salvajes", "La biología real supera a la ficción.",
    "Curiosos de 16–44 años interesados en animales, ciencia y hechos sorprendentes.",
    "Documental, intrigante, preciso y visualmente intenso; nunca infantil ni sensacionalista.",
    "#FFD447", "#07111B",
    "Vídeo real del animal como primera opción. Gráficos solo para explicar. IA visual opcional y etiquetada.",
    "Contradicción o pregunta en menos de 2 segundos, acompañada por el plano más específico del animal.",
    ["¿Tú qué piensas? Deja tu comentario ↓", "¿Te ha sorprendido? Cuéntame por qué ↓", "¿Lo sabías? Te leo en comentarios ↓", "¿Qué animal debería ser el siguiente? ↓"],
)

DEFAULT_NICHE = WILDLIFE_NICHE

DEFAULT_NICHES = [
    WILDLIFE_NICHE,
    Niche(
        "historia-oculta", "Historia Oculta", "El pasado fue más extraño de lo que recuerdas.",
        "Curiosos de 18–44 años atraídos por episodios históricos breves y sorprendentes.",
        "Cinematográfico, riguroso y misterioso; distingue hechos, hipótesis y leyendas.",
        "#FF7A59", "#120D12",
        "Archivo, recreaciones acreditadas y mapas. Nunca presentar una recreación como metraje real.",
        "Empieza con una consecuencia imposible de ignorar y revela cuándo y dónde ocurrió.",
        ["¿Conocías esta historia? Déjalo en comentarios ↓", "¿Qué episodio investigamos después? ↓", "¿Mito o historia? Te leo ↓"],
    ),
    Niche(
        "lugares-limite", "Lugares Límite", "Hay lugares reales que parecen inventados.",
        "Viajeros curiosos y amantes de la geografía, fenómenos naturales y paisajes extremos.",
        "Inmersivo, asombroso y preciso; prioriza escala, ubicación y experiencia sensorial.",
        "#31D7C8", "#061514",
        "Metraje real identificable, mapas mínimos y escala humana. Evitar paisajes genéricos repetidos.",
        "Abre dentro del lugar con el fenómeno ya ocurriendo y ubícalo antes del segundo cinco.",
        ["¿Entrarías aquí? Cuéntamelo ↓", "¿Qué lugar debería ser el siguiente? ↓", "¿Lo visitarías? Te leo ↓"],
    ),
    Niche(
        "ciencia-invisible", "Ciencia Invisible", "Lo cotidiano cambia cuando entiendes cómo funciona.",
        "Público general de 16–44 años que disfruta explicaciones visuales y aplicables.",
        "Claro, ingenioso y demostrable; una pregunta, un mecanismo y una conclusión.",
        "#62A8FF", "#08111F",
        "Demostraciones reales, macro y gráficos funcionales. Cada plano debe explicar una frase.",
        "Muestra primero el efecto cotidiano y formula la pregunta que el espectador nunca se hizo.",
        ["¿Qué cosa cotidiana explicamos después? ↓", "¿Ya lo habías notado? Te leo ↓", "Pruébalo y dime qué ves ↓"],
    ),
    Niche(
        "futuro-real", "Futuro Real", "Tecnología emergente sin humo ni promesas vacías.",
        "Personas de 18–44 años interesadas en tecnología, energía, medicina y el futuro cercano.",
        "Sobrio, visual y escéptico; separa prototipo, demostración y producto disponible.",
        "#B38CFF", "#100C1A",
        "Laboratorios, prototipos y diagramas acreditados. Etiquetar simulaciones y conceptos.",
        "Contrasta el titular espectacular con lo que la tecnología ya puede hacer hoy.",
        ["¿Avance real o demasiado pronto? Opina ↓", "¿Qué tecnología analizamos después? ↓", "¿La usarías? Te leo ↓"],
    ),
]


DEFAULT_IDEAS = [
    VideoIdea("octopus-neurons", "mentes-salvajes", "El pulpo que piensa con los brazos", "Inteligencia distribuida sin caer en el mito de los nueve cerebros.", "¿Un pulpo puede pensar con los brazos?", "Primerísimo plano de ventosas y tentáculos en movimiento.", 94, "media", 0.0, "renderizable", "octopus"),
    VideoIdea("crow-faces", "mentes-salvajes", "El cuervo que recuerda tu cara", "Memoria social y reconocimiento de amenazas durante años.", "Si molestas a este cuervo, puede recordarte durante años.", "Cuervo mirando directamente a cámara y siguiendo a una persona.", 92, "media", 0.12),
    VideoIdea("axolotl-regeneration", "mentes-salvajes", "El animal que reconstruye su propio cuerpo", "Regeneración de extremidades, tejidos y partes de órganos, explicada sin prometer inmortalidad.", "Puede reconstruir partes de su cuerpo sin dejar cicatriz.", "Macro real de un ajolote con branquias externas en movimiento.", 91, "media", 0.16),
    VideoIdea("wood-frog-freeze", "mentes-salvajes", "La rana que se congela y vuelve a vivir", "Supervivencia parcial a la congelación mediante crioprotectores naturales.", "Su corazón se detiene… y meses después vuelve a latir.", "Rana inmóvil entre hielo y posterior movimiento real.", 95, "alta", 0.22),
    VideoIdea("dolphin-half-sleep", "mentes-salvajes", "El animal que duerme con medio cerebro", "Sueño unihemisférico y respiración consciente.", "Si se durmiera como tú, podría ahogarse.", "Delfín saliendo a respirar mientras nada junto al grupo.", 90, "media", 0.10),
    VideoIdea("cuttlefish-disguise", "mentes-salvajes", "La piel que funciona como una pantalla", "Cromatóforos, textura y señales visuales de las sepias.", "Este animal cambia de aspecto antes de que puedas parpadear.", "Cambio real de patrón y textura en una sepia.", 93, "media", 0.14),
    VideoIdea("mantis-shrimp-punch", "mentes-salvajes", "El golpe que crea una explosión bajo el agua", "Golpe del camarón mantis y cavitación, evitando exageraciones comunes.", "Golpea tan rápido que el agua produce otra onda de choque.", "Macro de las patas raptoras seguido de impacto a cámara lenta.", 96, "alta", 0.28),
    VideoIdea("tardigrade-limits", "mentes-salvajes", "El animal casi indestructible… pero no inmortal", "Qué resisten realmente los tardígrados y dónde termina el mito.", "Sobrevive al espacio, pero un charco puede matarlo.", "Microscopía real de un tardígrado caminando.", 89, "alta", 0.24),
    VideoIdea("wombat-cubes", "mentes-salvajes", "Por qué los wombats hacen cubos", "La mecánica intestinal que produce excrementos cúbicos, tratada con tono documental.", "No existe otro animal que deje rastros con esta forma.", "Wombat caminando y gráfico anatómico muy breve.", 88, "baja", 0.08),
    VideoIdea("immortal-jellyfish", "mentes-salvajes", "La medusa que puede reiniciar su vida", "Transdiferenciación y límites reales de la llamada medusa inmortal.", "Cuando está en peligro, puede volver a ser joven.", "Medusa real pulsando, con ciclo de vida minimalista.", 94, "alta", 0.25),
    VideoIdea("electric-eel-hunt", "mentes-salvajes", "El pez que usa electricidad como un radar", "Descargas para detectar, inmovilizar y explorar el entorno.", "No solo electrocuta: también localiza lo que no puede ver.", "Anguila eléctrica real y visualización discreta del campo.", 90, "alta", 0.23),
    VideoIdea("orca-culture", "mentes-salvajes", "Las orcas también tienen cultura", "Técnicas de caza transmitidas dentro de grupos familiares.", "Dos grupos de orcas pueden vivir distinto, como dos culturas.", "Manada real coordinándose en superficie.", 91, "alta", 0.30),
    VideoIdea("roman-concrete", "historia-oculta", "El hormigón romano que repara sus grietas", "Qué sabemos sobre los clastos de cal y la autorreparación observada en formulaciones romanas.", "Esta grieta puede cerrarse sola gracias a una receta de hace 2.000 años.", "Macro de una grieta real seguido por una sección de hormigón antiguo.", 93, "media", 0.12),
    VideoIdea("molasses-flood", "historia-oculta", "La inundación que no era de agua", "El desastre de melaza de Boston de 1919 explicado con archivo, mapa y escala humana.", "Una ola pegajosa atravesó Boston más rápido de lo que muchos pudieron correr.", "Fotografía de archivo de la zona y una línea de altura superpuesta.", 95, "media", 0.10),
    VideoIdea("tyrian-purple", "historia-oculta", "El color que valía más que el oro", "Cómo se fabricaba la púrpura de Tiro y por qué estaba ligada al poder.", "Para teñir una túnica hacían falta miles de caracoles.", "Tela púrpura en macro y conchas identificables, sin recreaciones falsas.", 89, "media", 0.14),
    VideoIdea("dancing-plague", "historia-oculta", "La ciudad que no podía dejar de bailar", "El episodio de Estrasburgo de 1518 y las explicaciones propuestas, sin afirmar una causa cerrada.", "En 1518, decenas de personas bailaron durante días sin una explicación segura.", "Grabado histórico con fecha y mapa animado de Estrasburgo.", 96, "alta", 0.18),
    VideoIdea("blood-falls", "lugares-limite", "La cascada roja de la Antártida", "El origen salino y rico en hierro de Blood Falls, evitando presentarlo como sangre.", "Esto parece sangre saliendo de un glaciar, pero la explicación es aún más extraña.", "Plano real y cercano del flujo rojo sobre el hielo blanco.", 96, "alta", 0.25),
    VideoIdea("socotra-trees", "lugares-limite", "La isla con árboles de otro planeta", "Los dragos de Socotra, su forma, adaptación y aislamiento biológico.", "Estos árboles solo parecen imposibles hasta que entiendes dónde viven.", "Travelling real bajo una copa de drago con una persona para escala.", 92, "alta", 0.22),
    VideoIdea("danakil-colors", "lugares-limite", "El paisaje más tóxico parece pintado", "Los colores minerales y las condiciones extremas de Dallol, con advertencias de seguridad.", "Los colores más vivos de este paisaje nacen de química extrema.", "Charcas minerales reales con escala y rótulo de ubicación.", 91, "alta", 0.28),
    VideoIdea("svalbard-burials", "lugares-limite", "Por qué casi nadie es enterrado en Svalbard", "Qué hay de cierto en el mito de que morir está prohibido y cómo influyen el permafrost y la logística.", "No está prohibido morir aquí, pero la realidad es casi igual de extraña.", "Cementerio real de Longyearbyen y suelo helado en detalle.", 94, "media", 0.20),
    VideoIdea("petrichor", "ciencia-invisible", "Por qué la lluvia tiene olor", "Petrichor, geosmina y aerosoles liberados cuando las gotas golpean superficies porosas.", "Ese olor aparece antes de que veas la lluvia. ¿De dónde sale?", "Gota a cámara lenta golpeando tierra seca y macro de burbujas.", 93, "media", 0.08),
    VideoIdea("metal-smell", "ciencia-invisible", "El metal no huele como crees", "Por qué el olor metálico procede en gran parte de reacciones con compuestos de la piel.", "La moneda no huele a metal: gran parte de ese olor viene de ti.", "Dedos tocando una moneda y gráfico molecular muy breve.", 91, "baja", 0.05),
    VideoIdea("airplane-window-hole", "ciencia-invisible", "El pequeño agujero de la ventanilla del avión", "Cómo el orificio de respiración ayuda a gestionar la diferencia de presión entre paneles.", "Ese agujero diminuto ayuda a que la ventanilla soporte el vuelo.", "Macro real del orificio con capas de la ventanilla señaladas.", 95, "media", 0.10),
    VideoIdea("onion-tears", "ciencia-invisible", "Por qué una cebolla te hace llorar", "La química del factor lacrimógeno, explicada con una demostración visual sencilla.", "La cebolla fabrica este irritante justo cuando la cortas.", "Cuchillo atravesando células de cebolla en macro y reacción visual.", 88, "baja", 0.06),
    VideoIdea("solid-state-battery", "futuro-real", "La batería sólida no es magia", "Ventajas potenciales y obstáculos de fabricación antes de su adopción masiva.", "Promete más autonomía y menos riesgo, pero aún hay una barrera enorme.", "Celda real de laboratorio y corte de sus capas, etiquetado como diagrama.", 92, "alta", 0.24),
    VideoIdea("fusion-reality", "futuro-real", "Fusión: el récord no es una central eléctrica", "Diferencia entre ganancia experimental, energía total del sistema y electricidad comercial.", "Sí, hubo un hito de fusión. No, todavía no alimenta tu casa.", "Instalación real de laboratorio y balance energético animado.", 96, "alta", 0.30),
    VideoIdea("soft-robots", "futuro-real", "Robots que no necesitan huesos", "Robótica blanda inspirada en organismos flexibles y sus aplicaciones reales.", "Este robot no tiene articulaciones rígidas y por eso entra donde otros no pueden.", "Prototipo blando real agarrando un objeto delicado.", 90, "alta", 0.25),
    VideoIdea("photonic-chips", "futuro-real", "Chips que calculan con luz", "Qué tareas pueden acelerar los circuitos fotónicos y qué sigue dependiendo de electrónica.", "En este chip, parte de la información viaja como luz.", "Banco óptico real y guía de onda iluminada con rótulos mínimos.", 91, "alta", 0.28),
]


def ensure_library(root: Path) -> tuple[list[Niche], list[VideoIdea]]:
    root.mkdir(parents=True, exist_ok=True)
    niches_path, ideas_path = root / "niches.json", root / "ideas.json"
    stored_niches = _read_json(niches_path) if niches_path.exists() else []
    stored_ideas = _read_json(ideas_path) if ideas_path.exists() else []
    niche_slugs = {item["slug"] for item in stored_niches}
    idea_slugs = {item["slug"] for item in stored_ideas}
    merged_niches = stored_niches + [asdict(item) for item in DEFAULT_NICHES if item.slug not in niche_slugs]
    merged_ideas = stored_ideas + [asdict(item) for item in DEFAULT_IDEAS if item.slug not in idea_slugs]
    if merged_niches != stored_niches: _write_json(niches_path, merged_niches)
    if merged_ideas != stored_ideas: _write_json(ideas_path, merged_ideas)
    return [Niche(**item) for item in merged_niches], [VideoIdea(**item) for item in merged_ideas]


def add_niche(root: Path, niche: Niche) -> None:
    niches, _ = ensure_library(root)
    if any(item.slug == niche.slug for item in niches): raise ValueError("Ya existe un nicho con ese identificador.")
    _write_json(root / "niches.json", [asdict(item) for item in niches + [niche]])


def add_idea(root: Path, idea: VideoIdea) -> None:
    _, ideas = ensure_library(root)
    if any(item.slug == idea.slug for item in ideas): raise ValueError("Ya existe una idea con ese identificador.")
    _write_json(root / "ideas.json", [asdict(item) for item in ideas + [idea]])


def create_project(root: Path, idea: VideoIdea, niche: Niche, script: str, cta_index: int = 0) -> Path:
    project = root / "projects" / f"{datetime.now():%Y%m%d-%H%M%S}-{idea.slug}"
    project.mkdir(parents=True, exist_ok=False)
    package = publication_package(idea, niche, cta_index)
    record = {"created_at": datetime.now(timezone.utc).isoformat(), "status": "ready_to_render" if idea.renderer == "octopus" else "editorial_ready", "idea": asdict(idea), "niche": asdict(niche), "script": script.strip(), "publication": package, "budget": {"cap_usd": 0.50, "target_usd": 0.40, "estimated_usd": idea.estimated_cost_usd}}
    _write_json(project / "project.json", record)
    (project / "guion.txt").write_text(script.strip() + "\n", encoding="utf-8")
    (project / "publicacion.txt").write_text(format_publication(package), encoding="utf-8")
    return project


def publication_package(idea: VideoIdea, niche: Niche, cta_index: int = 0) -> dict:
    tags_by_niche = {
        "mentes-salvajes": ["#Animales", "#Biología", "#Naturaleza"],
        "historia-oculta": ["#Historia", "#HistoriaReal", "#Curiosidades"],
        "lugares-limite": ["#Geografía", "#LugaresIncreíbles", "#Viajes"],
        "ciencia-invisible": ["#Ciencia", "#CómoFunciona", "#Curiosidades"],
        "futuro-real": ["#Tecnología", "#Innovación", "#Futuro"],
    }
    hashtags = ["#Shorts", *tags_by_niche.get(niche.slug, ["#Curiosidades", "#Aprende"])]
    return {"title": idea.title[:70], "description": f"{idea.angle}\n\n{niche.promise} Suscríbete para descubrir el siguiente caso.", "hashtags": hashtags, "keywords": [niche.name.lower(), niche.promise.lower(), idea.title.lower()], "cta": niche.cta_variants[cta_index % len(niche.cta_variants)], "thumbnail": {"ratio": "9:16", "recommended_size": "2160x3840", "headline": _thumbnail_headline(idea), "brief": f"{niche.visual_policy} Plano de apertura: {idea.visual_hook} Fondo limpio, contraste alto y acento {niche.primary_color}."}, "upload_checklist": ["Confirmar cada afirmación con fuentes fiables.", "Revisar derechos y atribuciones de todos los clips.", "Comprobar subtítulos y zona segura en móvil.", "Seleccionar o subir la portada 9:16 en YouTube Studio.", "No presentar recreaciones o simulaciones como imágenes reales."]}


def render_octopus(repo_root: Path, project: Path, cta_index: int) -> Path:
    output = project / "video-final.mp4"
    shell = shutil.which("pwsh") or shutil.which("powershell")
    if not shell: raise FileNotFoundError("No se encontró PowerShell para ejecutar el render.")
    command = [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(repo_root / "scripts" / "render_octopus_short.ps1"), "-Output", str(output), "-CtaVariant", str(cta_index % 4)]
    completed = subprocess.run(command, cwd=repo_root, capture_output=True, text=True, timeout=900)
    if completed.returncode != 0 or not output.exists(): raise RuntimeError((completed.stderr or completed.stdout or "El render no produjo un MP4.").strip())
    return output


def create_cover(repo_root: Path, video: Path, output: Path, second: float = 1.0) -> Path:
    ffmpeg = next((repo_root / ".tools").rglob("ffmpeg*.exe"), None)
    if not ffmpeg: raise FileNotFoundError("FFmpeg no está instalado en .tools.")
    completed = subprocess.run([str(ffmpeg), "-y", "-hide_banner", "-loglevel", "error", "-ss", str(second), "-i", str(video), "-frames:v", "1", "-vf", "scale=2160:3840:flags=lanczos", str(output)], cwd=repo_root, capture_output=True, text=True, timeout=120)
    if completed.returncode != 0 or not output.exists(): raise RuntimeError((completed.stderr or "No se pudo generar la portada.").strip())
    return output


def list_projects(root: Path) -> Iterable[Path]:
    folder = root / "projects"
    return sorted((path for path in folder.glob("*") if path.is_dir()), reverse=True) if folder.exists() else []


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9áéíóúüñ]+", "-", value.lower().strip(), flags=re.IGNORECASE).strip("-")


def _thumbnail_headline(idea: VideoIdea) -> str:
    return " ".join(re.sub(r"[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9 ]", "", idea.hook).upper().split()[:5])


def format_publication(package: dict) -> str:
    return f"TÍTULO\n{package['title']}\n\nDESCRIPCIÓN\n{package['description']}\n\nHASHTAGS\n{' '.join(package['hashtags'])}\n\nCTA\n{package['cta']}\n\nPORTADA\n{package['thumbnail']['headline']}\n{package['thumbnail']['brief']}\n"


def _read_json(path: Path) -> list[dict]: return json.loads(path.read_text(encoding="utf-8"))
def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
