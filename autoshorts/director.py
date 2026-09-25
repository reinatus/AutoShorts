from __future__ import annotations

import re
from typing import Iterable

from .models import ChannelPreset, Scene, ShortPlan


DEMO_PLANS = {
    "la isla donde está prácticamente prohibido morir": {
        "hook": "En este remoto lugar del Ártico, morir es algo que las autoridades intentan evitar.",
        "beats": [
            ("Esto ocurre en Longyearbyen, el principal asentamiento de Svalbard, muy al norte de Noruega.", "Longyearbyen Svalbard Norway aerial winter town"),
            ("El frío extremo mantiene el suelo permanentemente congelado durante gran parte del año.", "Svalbard permafrost frozen ground arctic close up"),
            ("Por eso el cementerio local dejó de aceptar entierros tradicionales hace décadas.", "Longyearbyen cemetery Svalbard wooden crosses snow"),
            ("El problema no es una ley que castigue morir, sino las dificultades de enterrar cuerpos en el permafrost.", "Svalbard arctic cemetery winter documentary"),
            ("Cuando una persona está gravemente enferma, normalmente recibe atención o traslado al territorio continental noruego.", "Longyearbyen hospital Svalbard exterior winter"),
            ("La historia se ha convertido en el famoso mito de que aquí está prohibido morirse.", "Longyearbyen streets polar night people walking"),
            ("La realidad es menos absurda, pero bastante más inquietante: el hielo cambia incluso la forma de gestionar la muerte.", "Svalbard polar night cinematic landscape town lights"),
        ],
        "ending": ("Y todo esto ocurre en una de las poblaciones permanentes más septentrionales del planeta.", "Longyearbyen Svalbard aerial polar night mountains"),
    }
}


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def build_plan(subject: str, preset: ChannelPreset, manual_script: str = "") -> ShortPlan:
    """Build a deterministic storyboard.

    The demo topic ships with an editorially written plan. For arbitrary topics,
    users can provide a script; it is split into scenes and transformed into
    concrete search queries. An LLM provider can be plugged into this boundary
    later without coupling the UI to a vendor.
    """
    demo = DEMO_PLANS.get(_normalise(subject))
    if demo:
        lines = [demo["hook"]] + [x[0] for x in demo["beats"]] + [demo["ending"][0]]
        visual_queries = [
            "Longyearbyen Svalbard aerial arctic winter cinematic"
        ] + [x[1] for x in demo["beats"]] + [demo["ending"][1]]
        # Keep exactly the configured number of scenes while retaining the ending.
        if len(lines) > preset.scenes:
            lines = lines[: preset.scenes - 1] + [lines[-1]]
            visual_queries = visual_queries[: preset.scenes - 1] + [visual_queries[-1]]
        scenes = [
            Scene(i + 1, narration=line, visual_query=query, duration=preset.clip_duration)
            for i, (line, query) in enumerate(zip(lines, visual_queries))
        ]
        return ShortPlan(subject, demo["hook"], " ".join(lines), scenes)

    if not manual_script.strip():
        raise ValueError(
            "Para temas nuevos introduce un guion manual. El tema demo ya incluye storyboard completo."
        )

    chunks = _split_script(manual_script, preset.scenes)
    scenes = []
    for i, chunk in enumerate(chunks):
        query = f"{subject}, {chunk[:90]}, {preset.visual_style}"
        scenes.append(Scene(i + 1, chunk, query, preset.clip_duration))
    return ShortPlan(subject, chunks[0], " ".join(chunks), scenes)


def _split_script(script: str, max_scenes: int) -> list[str]:
    sentences = [x.strip() for x in re.split(r"(?<=[.!?])\s+", script.strip()) if x.strip()]
    if not sentences:
        return [script.strip()]
    if len(sentences) <= max_scenes:
        return sentences
    groups = [[] for _ in range(max_scenes)]
    for i, sentence in enumerate(sentences):
        groups[min(i * max_scenes // len(sentences), max_scenes - 1)].append(sentence)
    return [" ".join(group) for group in groups if group]
