from pathlib import Path

import io
import json
import zipfile

import pytest

from autoshorts.production import (
    MediaValidationError,
    build_storyboard,
    project_archive_bytes,
    save_media_manifest,
    set_project_status,
    sha256_bytes,
    validate_media_records,
)


def media(name: str, payload: bytes, relevance: str) -> dict:
    return {
        "filename": name,
        "size_bytes": len(payload),
        "sha256": sha256_bytes(payload),
        "source": "Material propio",
        "license": "Material propio",
        "relevance": relevance,
    }


def test_validated_media_builds_a_40_second_storyboard():
    records = validate_media_records(
        [
            media("hook.mp4", b"one", "Primer plano del sujeto"),
            media("detail.mov", b"two", "Detalle que explica el mecanismo"),
            media("close.webm", b"three", "Plano final documental"),
        ]
    )
    board = build_storyboard("uno dos tres cuatro cinco seis siete ocho nueve", "Gancho visual", records)

    assert len(board) == 3
    assert board[0]["start"] == 0
    assert board[-1]["end"] == 40
    assert board[0]["purpose"] == "Gancho visual"


def test_duplicate_or_undocumented_media_is_rejected():
    duplicate = media("a.mp4", b"same", "")
    with pytest.raises(MediaValidationError) as caught:
        validate_media_records([duplicate, {**duplicate, "filename": "b.mp4"}, media("c.mp4", b"other", "Cierre")])

    assert "repetido" in str(caught.value)
    assert "falta explicar" in str(caught.value)


def test_manifest_and_status_are_persisted(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "project.json").write_text(json.dumps({"status": "editorial_ready"}), encoding="utf-8")
    records = [
        media("one.mp4", b"one", "Uno"),
        media("two.mp4", b"two", "Dos"),
        media("three.mp4", b"three", "Tres"),
    ]
    board = build_storyboard("texto de prueba", "Gancho", records)

    manifest = save_media_manifest(project, records, board)
    set_project_status(project, "failed", "fallo controlado")

    assert manifest.exists()
    saved = json.loads(manifest.read_text(encoding="utf-8"))
    assert saved["rights_reviewed"] is True
    status = json.loads((project / "project.json").read_text(encoding="utf-8"))
    assert status["status"] == "failed"
    assert status["last_error"] == "fallo controlado"


def test_delivery_zip_contains_only_final_assets(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "video-final.mp4").write_bytes(b"video")
    (project / "portada-9x16.jpg").write_bytes(b"cover")
    (project / "publicacion.txt").write_text("metadata", encoding="utf-8")
    (project / "unrelated.tmp").write_text("ignore", encoding="utf-8")

    payload = project_archive_bytes(project)
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        assert set(archive.namelist()) == {"video-final.mp4", "portada-9x16.jpg", "publicacion.txt"}
