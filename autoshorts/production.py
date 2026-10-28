from __future__ import annotations

import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".webm"}
MAX_CLIP_BYTES = 300 * 1024 * 1024
MAX_TOTAL_BYTES = 1024 * 1024 * 1024
MAX_CLIPS = 12


class MediaValidationError(ValueError):
    """Raised when a media batch is not safe or sufficiently documented."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def validate_media_records(records: Iterable[dict]) -> list[dict]:
    clean: list[dict] = []
    errors: list[str] = []
    seen_hashes: set[str] = set()
    total_size = 0

    for index, raw in enumerate(records, 1):
        name = Path(str(raw.get("filename", ""))).name
        suffix = Path(name).suffix.lower()
        size = int(raw.get("size_bytes", 0) or 0)
        digest = str(raw.get("sha256", "")).lower().strip()
        source = str(raw.get("source", "")).strip()
        license_name = str(raw.get("license", "")).strip()
        relevance = str(raw.get("relevance", "")).strip()

        if not name or suffix not in ALLOWED_VIDEO_EXTENSIONS:
            errors.append(f"Clip {index}: formato no permitido ({name or 'sin nombre'}).")
        if size <= 0:
            errors.append(f"Clip {index}: el archivo esta vacio.")
        elif size > MAX_CLIP_BYTES:
            errors.append(f"Clip {index}: supera 300 MB.")
        if digest and digest in seen_hashes:
            errors.append(f"Clip {index}: esta repetido.")
        if not source:
            errors.append(f"Clip {index}: falta la fuente o propietario.")
        if not license_name:
            errors.append(f"Clip {index}: falta indicar la licencia.")
        if not relevance:
            errors.append(f"Clip {index}: falta explicar que muestra.")

        if digest:
            seen_hashes.add(digest)
        total_size += max(0, size)
        clean.append(
            {
                "filename": name,
                "size_bytes": size,
                "sha256": digest,
                "source": source,
                "license": license_name,
                "relevance": relevance,
            }
        )

    if len(clean) < 3:
        errors.append("Se necesitan al menos tres clips diferentes.")
    if len(clean) > MAX_CLIPS:
        errors.append(f"Se admiten como maximo {MAX_CLIPS} clips por Short.")
    if total_size > MAX_TOTAL_BYTES:
        errors.append("El conjunto de clips supera 1 GB.")
    if errors:
        raise MediaValidationError("\n".join(errors))
    return clean


def build_storyboard(script: str, visual_hook: str, media_records: list[dict], duration: float = 40.0) -> list[dict]:
    if not media_records:
        return []
    words = script.replace("\n", " ").split()
    count = len(media_records)
    seconds = duration / count
    storyboard = []
    for index, record in enumerate(media_records):
        word_start = round(len(words) * index / count)
        word_end = round(len(words) * (index + 1) / count)
        narration = " ".join(words[word_start:word_end]).strip()
        storyboard.append(
            {
                "scene": index + 1,
                "start": round(index * seconds, 2),
                "end": round((index + 1) * seconds, 2),
                "clip": record["filename"],
                "purpose": visual_hook if index == 0 else record["relevance"],
                "narration": narration,
            }
        )
    return storyboard


def save_media_manifest(project: Path, records: list[dict], storyboard: list[dict]) -> Path:
    output = project / "media-manifest.json"
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "rights_reviewed": True,
        "clips": records,
        "storyboard": storyboard,
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


def set_project_status(project: Path, status: str, error: str | None = None) -> None:
    record_path = project / "project.json"
    if not record_path.exists():
        return
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record["status"] = status
    record["updated_at"] = datetime.now(timezone.utc).isoformat()
    if error:
        record["last_error"] = error[-2000:]
    else:
        record.pop("last_error", None)
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


DELIVERY_FILES = (
    "video-final.mp4",
    "portada-9x16.jpg",
    "guion.txt",
    "publicacion.txt",
    "project.json",
    "media-manifest.json",
    "subtitulos.ass",
)


def project_archive_bytes(project: Path) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for filename in DELIVERY_FILES:
            path = project / filename
            if path.is_file():
                archive.write(path, arcname=filename)
    return buffer.getvalue()
