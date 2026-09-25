from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List


@dataclass
class ChannelPreset:
    slug: str
    name: str
    language: str = "es"
    min_duration: int = 35
    max_duration: int = 50
    scenes: int = 8
    voice_name: str = "es-ES-AlvaroNeural-Male"
    voice_rate: float = 1.08
    bgm_volume: float = 0.12
    clip_duration: int = 5
    visual_style: str = "realistic documentary, cinematic, high detail, vertical composition"
    editorial_rules: List[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


@dataclass
class Scene:
    index: int
    narration: str
    visual_query: str
    duration: float = 5.0

    def to_dict(self):
        return asdict(self)


@dataclass
class ShortPlan:
    subject: str
    hook: str
    script: str
    scenes: List[Scene]

    @property
    def visual_terms(self) -> List[str]:
        return [scene.visual_query for scene in self.scenes]

    def to_dict(self):
        data = asdict(self)
        data["visual_terms"] = self.visual_terms
        return data
