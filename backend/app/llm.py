from __future__ import annotations

from dataclasses import dataclass
from .models import LLMConfig


@dataclass
class LLMProvider:
    config: LLMConfig

    def switch_mode(self, new_config: LLMConfig) -> None:
        self.config = new_config

    def generate(self, prompt: str, speaker_name: str) -> str:
        # MVP: deterministic style output, preserving cloud/local abstraction.
        if self.config.mode == "local":
            return f"【本地模型-{self.config.provider}】{speaker_name}：{prompt[:48]}...我先保留一点判断。"
        return f"【云端模型-{self.config.provider}】{speaker_name}：{prompt[:48]}...我倾向于继续观察。"
