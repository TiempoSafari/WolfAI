from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class Phase(str, Enum):
    PREPARATION = "preparation"
    NIGHT = "night"
    DAY = "day"
    VOTING = "voting"
    CONCLUSION = "conclusion"


class Role(str, Enum):
    VILLAGER = "villager"
    WEREWOLF = "werewolf"
    SEER = "seer"
    WITCH = "witch"


class LLMMode(str, Enum):
    CLOUD = "cloud"
    LOCAL = "local"


class LLMConfig(BaseModel):
    mode: LLMMode = LLMMode.CLOUD
    provider: str = "qwen"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = "qwen-turbo"
    temperature: float = 0.7
    max_tokens: int = 256


class Player(BaseModel):
    player_id: str
    name: str
    role: Role
    is_human: bool = False
    is_alive: bool = True


class Speech(BaseModel):
    player_id: str
    text: str


class GameState(BaseModel):
    game_id: str
    phase: Phase = Phase.DAY
    day_number: int = 1
    players: List[Player]
    alive_players: List[str] = Field(default_factory=list)
    eliminated_players: List[str] = Field(default_factory=list)
    speeches: List[Speech] = Field(default_factory=list)
    latest_event: str = ""
    winner: Optional[Literal["good", "wolf"]] = None
    llm_config: LLMConfig = Field(default_factory=LLMConfig)


class CreateGameRequest(BaseModel):
    human_name: str = "你"
    mode: Literal["quick"] = "quick"


class VoteRequest(BaseModel):
    target_player_id: str


class SwitchLLMRequest(BaseModel):
    mode: LLMMode
    provider: str
    base_url: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None
