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


DEFAULT_NICHE = Niche(
    "mentes-salvajes", "Mentes Salvajes", "La biología real supera a la ficción.",
    "Curiosos de 16–44 años interesados en animales, ciencia y hechos sorprendentes.",
    "Documental, intrigante, preciso y visualmente intenso; nunca infantil ni sensacionalista.",
    "#FFD447", "#07111B",
    "Vídeo real del animal como primera opción. Gráficos solo para explicar. IA visual opcional y etiquetada.",
    "Contradicción o pregunta en menos de 2 segundos, acompañada por el plano más específico del animal.",
    ["¿Tú qué piensas? Deja tu comentario ↓", "¿Te ha sorprendido? Cuéntame por qué ↓", "¿Lo sabías? Te leo en comentarios ↓", "¿Qué animal debería ser el siguiente? ↓"],
)


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
]


def ensure_library(root: Path) -> tuple[list[Niche], list[VideoIdea]]:
    root.mkdir(parents=True, exist_ok=True)
    niches_path, ideas_path = root / "niches.json", root / "ideas.json"
    if not niches_path.exists(): _write_json(niches_path, [asdict(DEFAULT_NICHE)])
    if not ideas_path.exists(): _write_json(ideas_path, [asdict(item) for item in DEFAULT_IDEAS])
    return [Niche(**item) for item in _read_json(niches_path)], [VideoIdea(**item) for item in _read_json(ideas_path)]


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
    return {"title": idea.title[:70], "description": f"{idea.angle}\n\n{niche.promise} Suscríbete para descubrir el siguiente caso.", "hashtags": ["#Shorts", "#Animales", "#Ciencia", "#Naturaleza", "#Curiosidades"], "keywords": ["animales sorprendentes", "biología", "ciencia", idea.title.lower()], "cta": niche.cta_variants[cta_index % len(niche.cta_variants)], "thumbnail": {"ratio": "9:16", "recommended_size": "2160x3840", "headline": _thumbnail_headline(idea), "brief": f"Plano real, muy cerrado y reconocible: {idea.visual_hook} Fondo limpio, contraste alto, amarillo {niche.primary_color}, sin inventar anatomía."}, "upload_checklist": ["Confirmar que cada afirmación científica tiene fuente.", "Revisar derechos y atribuciones de todos los clips.", "Comprobar subtítulos y zona segura en móvil.", "Seleccionar o subir la portada 9:16 en YouTube Studio.", "No prometer hechos que el vídeo no demuestra."]}


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
