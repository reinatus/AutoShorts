from __future__ import annotations

import re

from .models import ChannelPreset, Scene, ShortPlan


REALISM_SUFFIX = (
    "photorealistic documentary video, authentic geography and architecture, natural lighting, "
    "physically plausible movement, subtle handheld or drone camera motion, real lens behavior, "
    "no CGI look, no illustration, no text, no logos, no fantasy elements, vertical 9:16"
)

DEMO_PLANS = {
    "la isla donde está prácticamente prohibido morir": {
        "hook": "En este remoto lugar del Ártico, morir es algo que las autoridades intentan evitar.",
        "beats": [
            ("Esto ocurre en Longyearbyen, el principal asentamiento de Svalbard, muy al norte de Noruega.", "real aerial documentary footage of Longyearbyen Svalbard in winter, recognizable town layout, mountains and fjord, slow drone push forward", True),
            ("El frío extremo mantiene el suelo permanentemente congelado durante gran parte del año.", "macro and ground-level documentary shot of Arctic permafrost near Longyearbyen, frozen soil and snow, gloved researcher examining ground", False),
            ("Por eso el cementerio local dejó de aceptar entierros tradicionales hace décadas.", "authentic documentary view of Longyearbyen cemetery in Svalbard, simple wooden crosses in snow, surrounding Arctic mountains, slow stabilized camera movement", True),
            ("El problema no es una ley que castigue morir, sino las dificultades de enterrar cuerpos en el permafrost.", "documentary reconstruction showing frozen Arctic ground and cemetery environment in Svalbard, respectful non-graphic scene, cold wind moving snow", False),
            ("Cuando una persona está gravemente enferma, normalmente recibe atención o traslado al territorio continental noruego.", "realistic exterior documentary shot of healthcare building in Longyearbyen during winter, bundled residents, snow, emergency transport atmosphere, no invented signage", True),
            ("La historia se ha convertido en el famoso mito de que aquí está prohibido morirse.", "street-level documentary footage in Longyearbyen polar night, real Arctic town architecture, pedestrians in winter clothing, practical lights, gentle handheld motion", True),
            ("La realidad es menos absurda, pero bastante más inquietante: el hielo cambia incluso la forma de gestionar la muerte.", "cinematic but realistic Svalbard polar night landscape overlooking Longyearbyen, town lights, snow and mountains, slow natural camera pan", False),
        ],
        "ending": ("Y todo esto ocurre en una de las poblaciones permanentes más septentrionales del planeta.", "wide photorealistic aerial of Longyearbyen and surrounding Svalbard wilderness at blue hour, slow drone pullback", False),
    }
}


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _prompt(base: str) -> str:
    return f"{base}. {REALISM_SUFFIX}"


def build_plan(subject: str, preset: ChannelPreset, manual_script: str = "") -> ShortPlan:
    demo = DEMO_PLANS.get(_normalise(subject))
    if demo:
        rows = [(demo["hook"], "establishing documentary shot of Longyearbyen Svalbard Arctic winter, recognizable settlement between mountains and fjord, dramatic but natural polar light", True)]
        rows += list(demo["beats"])
        rows += [demo["ending"]]
        if len(rows) > preset.scenes:
            rows = rows[: preset.scenes - 1] + [rows[-1]]
        scenes = []
        for i, (narration, visual, factual) in enumerate(rows):
            # Specific landmarks/locations are marked for real footage by default.
            # Generated video remains an explicit fallback and must be labelled as recreation.
            mode = "real_footage" if factual else "generated_video"
            scenes.append(Scene(
                index=i + 1,
                narration=narration,
                visual_query=_prompt(visual),
                duration=preset.clip_duration,
                visual_mode=mode,
                factual_visual=factual,
                on_screen_label="RECREACIÓN IA" if mode == "generated_video" else "",
            ))
        return ShortPlan(subject, demo["hook"], " ".join(x.narration for x in scenes), scenes)

    if not manual_script.strip():
        raise ValueError("Para temas nuevos introduce un guion manual. El tema demo ya incluye storyboard completo.")

    chunks = _split_script(manual_script, preset.scenes)
    scenes = []
    for i, chunk in enumerate(chunks):
        visual = _prompt(f"documentary scene directly illustrating this narration: {chunk[:160]}; subject: {subject}")
        scenes.append(Scene(i + 1, chunk, visual, preset.clip_duration, "generated_video", False, "RECREACIÓN IA"))
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
