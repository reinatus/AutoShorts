from .models import ChannelPreset


PRESETS = {
    "lugares-extranos": ChannelPreset(
        slug="lugares-extranos",
        name="Lugares extraños",
        language="es",
        min_duration=35,
        max_duration=50,
        scenes=8,
        voice_name="es-ES-AlvaroNeural-Male",
        voice_rate=1.08,
        bgm_volume=0.12,
        clip_duration=5,
        visual_style="3D cartoon cinematográfico",
        editorial_rules=[
            "Abrir con una afirmación sorprendente en menos de 3 segundos.",
            "No usar introducciones del tipo '¿Sabías que?'.",
            "Una idea visual concreta por escena.",
            "Mantener exactamente la misma dirección artística en todas las escenas.",
            "Usar nombres propios y detalles reales como referencia del contenido, pero renderizarlos en el estilo del canal.",
            "No repetir la misma información con otras palabras.",
            "Cerrar con un dato final que recompense haber visto el vídeo.",
            "No inventar hechos; los temas deben verificarse antes de publicarse.",
        ],
    )
}


def get_preset(slug: str) -> ChannelPreset:
    if slug not in PRESETS:
        raise KeyError(f"Canal desconocido: {slug}")
    return PRESETS[slug]
