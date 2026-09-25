from __future__ import annotations

import os
import time
from urllib.parse import urljoin

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
        # MoneyPrinterTurbo expects x-api-key when app.api_key is configured.
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    def health(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/ping", timeout=5)
            return response.ok
        except requests.RequestException:
            return False

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

    @staticmethod
    def extract_task_id(result: dict) -> str:
        data = result.get("data", result)
        for key in ("task_id", "id"):
            value = data.get(key) if isinstance(data, dict) else None
            if value:
                return str(value)
        raise ValueError(f"MoneyPrinterTurbo no devolvió task_id: {result}")

    def wait_for_video(self, task_id: str, timeout: int = 1800, interval: int = 5) -> dict:
        deadline = time.time() + timeout
        last = {}
        while time.time() < deadline:
            last = self.task(task_id)
            data = last.get("data", last)
            state = str(data.get("state") or data.get("status") or "").lower() if isinstance(data, dict) else ""
            if state in {"success", "completed", "complete", "done"}:
                return last
            if state in {"failed", "error", "cancelled", "canceled"}:
                raise RuntimeError(f"MoneyPrinterTurbo terminó con estado {state}: {last}")
            time.sleep(interval)
        raise TimeoutError(f"El render superó {timeout}s. Último estado: {last}")

    def video_urls(self, task_result: dict) -> list[str]:
        data = task_result.get("data", task_result)
        if not isinstance(data, dict):
            return []
        candidates = []
        for key in ("videos", "video_files", "video_urls", "combined_videos"):
            value = data.get(key)
            if isinstance(value, str):
                candidates.append(value)
            elif isinstance(value, list):
                candidates.extend(x for x in value if isinstance(x, str))
        return [x if x.startswith(("http://", "https://")) else urljoin(self.base_url + "/", x.lstrip("/")) for x in candidates]
