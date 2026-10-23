from pathlib import Path

from autoshorts.studio import DEFAULT_IDEAS, DEFAULT_NICHE, create_project, ensure_library, publication_package


def test_default_library_has_expandable_niche_and_ideas(tmp_path: Path):
    niches, ideas = ensure_library(tmp_path)
    assert niches[0].slug == "mentes-salvajes"
    assert len(ideas) >= 10
    assert any(item.renderer == "octopus" for item in ideas)


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
