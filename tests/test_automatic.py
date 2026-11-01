from autoshorts.automatic import _candidate_matches, automatic_script, media_queries
from autoshorts.free_media import MediaCandidate
from autoshorts.studio import DEFAULT_IDEAS, DEFAULT_NICHES


def test_automatic_script_has_no_manual_placeholder():
    idea = next(item for item in DEFAULT_IDEAS if item.slug == "crow-faces")
    niche = next(item for item in DEFAULT_NICHES if item.slug == idea.niche_slug)
    script = automatic_script(idea, niche)
    assert idea.hook in script
    assert idea.angle in script
    assert "[" not in script
    assert len(script.split()) >= 70


def test_every_default_idea_has_automatic_search_queries():
    for idea in DEFAULT_IDEAS:
        queries = media_queries(idea)
        assert len(queries) >= 4
        assert all("video" in query or "webm" in query for query in queries)


def test_music_results_are_not_accepted_as_animal_footage():
    candidate = MediaCandidate(
        title="File:Sheryl Crow concert.webm",
        url="https://example.test/crow.webm",
        page_url="https://example.test/page",
        mime="video/webm",
        license_name="CC BY",
        license_url="https://example.test/license",
        artist="Example",
        score=1.0,
    )
    assert not _candidate_matches(candidate, ("crow", "raven"))

