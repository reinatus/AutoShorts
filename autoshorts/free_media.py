from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import requests

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "AutoShorts/0.2 (specific free media resolver)"
VIDEO_EXTENSIONS = {".webm", ".ogv", ".mp4"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


@dataclass
class MediaCandidate:
    title: str
    url: str
    page_url: str
    mime: str
    license_name: str
    license_url: str
    artist: str
    score: float

    @property
    def is_video(self) -> bool:
        return self.mime.startswith("video/") or Path(urlparse(self.url).path).suffix.lower() in VIDEO_EXTENSIONS


def _tokens(text: str) -> set[str]:
    return {x.lower() for x in text.replace("_", " ").replace("-", " ").split() if len(x) > 2}


def _score(query: str, title: str, mime: str) -> float:
    q = _tokens(query)
    t = _tokens(title)
    overlap = len(q & t) / max(1, len(q))
    video_bonus = 0.25 if mime.startswith("video/") else 0.0
    return overlap + video_bonus


def search_commons(query: str, limit: int = 12) -> list[MediaCandidate]:
    params = {
        "action": "query", "generator": "search", "gsrsearch": query,
        "gsrnamespace": 6, "gsrlimit": limit, "prop": "imageinfo",
        "iiprop": "url|mime|extmetadata", "format": "json", "origin": "*",
    }
    r = requests.get(COMMONS_API, params=params, headers={"User-Agent": USER_AGENT}, timeout=20)
    r.raise_for_status()
    pages = r.json().get("query", {}).get("pages", {})
    out: list[MediaCandidate] = []
    for page in pages.values():
        info = (page.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata") or {}
        mime = info.get("mime") or ""
        url = info.get("url") or ""
        if not url or not (mime.startswith("video/") or mime.startswith("image/")):
            continue
        license_name = (meta.get("LicenseShortName") or {}).get("value", "")
        if not license_name:
            continue
        out.append(MediaCandidate(
            title=page.get("title", ""), url=url,
            page_url=info.get("descriptionurl") or "", mime=mime,
            license_name=license_name,
            license_url=(meta.get("LicenseUrl") or {}).get("value", ""),
            artist=(meta.get("Artist") or {}).get("value", ""),
            score=_score(query, page.get("title", ""), mime),
        ))
    return sorted(out, key=lambda x: x.score, reverse=True)


def best_specific_media(query: str, minimum_score: float = 0.30) -> MediaCandidate | None:
    items = search_commons(query)
    return items[0] if items and items[0].score >= minimum_score else None


def download(candidate: MediaCandidate, folder: str, stem: str) -> str:
    os.makedirs(folder, exist_ok=True)
    suffix = Path(urlparse(candidate.url).path).suffix.lower() or (".webm" if candidate.is_video else ".jpg")
    target = Path(folder) / f"{stem}{suffix}"
    with requests.get(candidate.url, headers={"User-Agent": USER_AGENT}, stream=True, timeout=60) as r:
        r.raise_for_status()
        with target.open("wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                if chunk:
                    f.write(chunk)
    return str(target)
