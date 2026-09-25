from __future__ import annotations

import base64
import os
from pathlib import Path

import requests


STYLE_PRESETS = {
    "3D cartoon cinematográfico": "cinematic stylized 3D cartoon, premium animated-film look, miniature diorama aesthetic, expressive shapes, detailed environments, soft volumetric lighting, shallow depth of field, consistent materials, polished render, no text, no watermark",
    "Cartoon ilustrado": "high-end editorial cartoon illustration, clean shapes, expressive lighting, detailed background, cohesive color palette, consistent illustration style, no text, no watermark",
    "Pixel art cinematográfico": "high-detail cinematic pixel art, consistent pixel grid, rich lighting, atmospheric depth, coherent palette, detailed environment, no text, no watermark",
    "Diorama 3D": "high-end miniature 3D diorama, tilt-shift composition, handcrafted materials, cinematic lighting, detailed environment, consistent scale, no text, no watermark",
}


class LocalImageGenerator:
    """OpenVINO Model Server client using its OpenAI-compatible image endpoint."""

    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = (base_url or os.getenv("IMAGE_API_URL") or "http://127.0.0.1:8000").rstrip("/")
        self.model = model or os.getenv("IMAGE_MODEL") or "OpenVINO/stable-diffusion-v1-5-int8-ov"

    def health(self) -> bool:
        for endpoint in ("/v3/models", "/v1/models"):
            try:
                if requests.get(self.base_url + endpoint, timeout=3).ok:
                    return True
            except requests.RequestException:
                pass
        return False

    def generate(self, scene_prompt: str, style_name: str, output: str, seed: int = 1337) -> str:
        style = STYLE_PRESETS[style_name]
        prompt = f"{scene_prompt}. {style}. vertical composition for a 9:16 short, same art direction across every scene"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "size": "512x768",
            "n": 1,
            "response_format": "b64_json",
            "seed": seed,
        }
        r = requests.post(self.base_url + "/v3/images/generations", json=payload, timeout=900)
        r.raise_for_status()
        item = r.json()["data"][0]
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        if item.get("b64_json"):
            Path(output).write_bytes(base64.b64decode(item["b64_json"]))
        elif item.get("url"):
            img = requests.get(item["url"], timeout=120)
            img.raise_for_status()
            Path(output).write_bytes(img.content)
        else:
            raise RuntimeError("El generador no devolvió una imagen")
        return output
