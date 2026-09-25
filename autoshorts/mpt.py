from __future__ import annotations

import os
import requests
from dotenv import load_dotenv

from .models import ChannelPreset, ShortPlan

load_dotenv()


class MoneyPrinterTurboClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = (base_url or os.getenv("MPT_API_URL") or "http://127.0.0.1:8080").rstrip("/")
        self.api_key = api_key if api_key is not None else os.getenv("MPT_API_KEY", "")

    @property
    def headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def payload(self, plan: ShortPlan, preset: ChannelPreset) -> dict:
        return {
            "video_subject": plan.subject,
            "video_script": plan.script,
            "video_terms": plan.visual_terms,
            "video_aspect": "9:16",
            "video_fit_mode": "cover",
            "video_concat_mode": "sequential",
            "video_transition_mode": "Shuffle",
            "video_clip_duration": preset.clip_duration,
            "video_count": 1,
            "video_source": "pexels",
            "video_language": preset.language,
            "voice_name": preset.voice_name,
            "voice_rate": preset.voice_rate,
            "voice_volume": 1.0,
            "bgm_type": "random",
            "bgm_volume": preset.bgm_volume,
            "subtitle_enabled": True,
            "subtitle_position": "two_thirds_bottom",
            "subtitle_display_mode": "word_by_word",
            "subtitle_animation": "pop_spring",
            "font_size": 72,
            "stroke_width": 2.0,
            "match_materials_to_script": True,
            "paragraph_number": 1,
        }

    def create_video(self, plan: ShortPlan, preset: ChannelPreset) -> dict:
        response = requests.post(
            f"{self.base_url}/api/v1/videos",
            headers=self.headers,
            json=self.payload(plan, preset),
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def task(self, task_id: str) -> dict:
        response = requests.get(
            f"{self.base_url}/api/v1/tasks/{task_id}",
            headers=self.headers,
            timeout=15,
        )
        response.raise_for_status()
        return response.json()
