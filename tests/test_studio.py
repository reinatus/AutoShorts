from pathlib import Path

import json

from autoshorts.studio import DEFAULT_IDEAS, DEFAULT_NICHE, _ass_subtitles, create_project, ensure_library, publication_package, render_uploaded_short


def test_default_library_has_expandable_niche_and_ideas(tmp_path: Path):
    niches, ideas = ensure_library(tmp_path)
    assert niches[0].slug == "mentes-salvajes"
    assert len(niches) >= 5
    assert len({item.niche_slug for item in ideas}) >= 5
    assert len(ideas) >= 25
    assert any(item.renderer == "octopus" for item in ideas)


def test_existing_library_is_migrated_without_losing_custom_data(tmp_path: Path):
    custom_niche = {**DEFAULT_NICHE.__dict__, "slug": "mi-canal", "name": "Mi canal"}
    custom_idea = {**DEFAULT_IDEAS[0].__dict__, "slug": "mi-idea", "niche_slug": "mi-canal"}
    (tmp_path / "niches.json").write_text(json.dumps([custom_niche]), encoding="utf-8")
    (tmp_path / "ideas.json").write_text(json.dumps([custom_idea]), encoding="utf-8")

    niches, ideas = ensure_library(tmp_path)

    assert any(item.slug == "mi-canal" for item in niches)
    assert any(item.slug == "mi-idea" for item in ideas)
    assert any(item.slug == "futuro-real" for item in niches)


def test_publication_package_is_complete():
    package = publication_package(DEFAULT_IDEAS[0], DEFAULT_NICHE, 1)
    assert package["title"] and package["description"]
    assert "#Shorts" in package["hashtags"]
    assert package["thumbnail"]["ratio"] == "9:16"
    assert package["cta"] == DEFAULT_NICHE.cta_variants[1]


def test_project_contains_budget_and_upload_text(tmp_path: Path):
    project = create_project(tmp_path, DEFAULT_IDEAS[0], DEFAULT_NICHE, "Guion de prueba", 0)
    assert (project / "project.json").exists()
    assert (project / "publicacion.txt").read_text(encoding="utf-8").startswith("TÍTULO")


def test_uploaded_renderer_requires_visual_variety(tmp_path: Path):
    try:
        render_uploaded_short(tmp_path, tmp_path, [tmp_path / "one.mp4"], "Guion", "Comenta")
    except ValueError as error:
        assert "tres clips" in str(error)
    else:
        raise AssertionError("El render debe impedir montajes con un solo clip.")


def test_subtitles_include_body_and_final_cta():
    subtitles = _ass_subtitles("Una explicación breve que se reparte en subtítulos legibles.", "¿Qué piensas?")
    assert "Style: Body" in subtitles
    assert "0:00:36.50,0:00:40.00,CTA" in subtitles
    assert "¿Qué piensas?" in subtitles
