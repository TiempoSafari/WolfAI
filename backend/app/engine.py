from __future__ import annotations

import random
import uuid
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List

from .llm import LLMProvider
from .models import GameState, LLMConfig, Phase, Player, Role, Speech


@dataclass
class GameEngine:
    games: Dict[str, GameState] = field(default_factory=dict)
    llm_providers: Dict[str, LLMProvider] = field(default_factory=dict)

    def create_quick_game(self, human_name: str) -> GameState:
        game_id = str(uuid.uuid4())
        names = [human_name, "阿尔法", "贝塔", "伽马", "德尔塔", "伊普西龙"]
        roles = [Role.WEREWOLF, Role.WEREWOLF, Role.SEER, Role.WITCH, Role.VILLAGER, Role.VILLAGER]
        random.shuffle(roles)

        players = [
            Player(player_id=f"p{i+1}", name=names[i], role=roles[i], is_human=(i == 0))
            for i in range(6)
        ]

        state = GameState(game_id=game_id, players=players, phase=Phase.DAY)
        self._refresh_alive_lists(state)
        state.latest_event = "游戏开始：第1天白天，请发言并投票。"
        self.games[game_id] = state
        self.llm_providers[game_id] = LLMProvider(config=state.llm_config)
        return state

    def get(self, game_id: str) -> GameState:
        return self.games[game_id]

    def switch_llm(self, game_id: str, config: LLMConfig) -> GameState:
        state = self.get(game_id)
        state.llm_config = config
        self.llm_providers[game_id].switch_mode(config)
        return state

    def generate_day_speeches(self, game_id: str) -> GameState:
        state = self.get(game_id)
        if state.phase != Phase.DAY:
            return state

        provider = self.llm_providers[game_id]
        state.speeches = []
        alive = [p for p in state.players if p.is_alive]
        for p in alive:
            if p.is_human:
                continue
            hint = "我觉得可疑的人需要在投票阶段重点关注"
            text = provider.generate(hint, p.name)
            state.speeches.append(Speech(player_id=p.player_id, text=text))

        state.phase = Phase.VOTING
        state.latest_event = "AI发言完成，请你投票。"
        return state

    def vote_and_advance(self, game_id: str, human_target: str) -> GameState:
        state = self.get(game_id)
        if state.phase != Phase.VOTING:
            return state

        alive_players = [p for p in state.players if p.is_alive]
        alive_ids = [p.player_id for p in alive_players]
        votes: List[str] = [human_target]

        for p in alive_players:
            if p.is_human:
                continue
            choices = [x for x in alive_ids if x != p.player_id]
            votes.append(random.choice(choices))

        out_id, _ = Counter(votes).most_common(1)[0]
        out_player = next(p for p in state.players if p.player_id == out_id)
        out_player.is_alive = False
        state.eliminated_players.append(out_id)

        self._check_winner(state)
        if state.winner:
            state.phase = Phase.CONCLUSION
            state.latest_event = f"{out_player.name}被放逐，游戏结束。"
            self._refresh_alive_lists(state)
            return state

        night_msg = self._resolve_night(state)
        self._check_winner(state)
        state.phase = Phase.CONCLUSION if state.winner else Phase.DAY
        state.day_number += 1 if not state.winner else 0
        state.latest_event = f"{out_player.name}被放逐。{night_msg}"
        self._refresh_alive_lists(state)
        return state

    def _resolve_night(self, state: GameState) -> str:
        wolves = [p for p in state.players if p.is_alive and p.role == Role.WEREWOLF]
        targets = [p for p in state.players if p.is_alive and p.role != Role.WEREWOLF]
        if not wolves or not targets:
            return "夜晚平安。"
        victim = random.choice(targets)
        victim.is_alive = False
        state.eliminated_players.append(victim.player_id)
        return f"夜晚结束，{victim.name}倒下。"

    def _check_winner(self, state: GameState) -> None:
        wolves = [p for p in state.players if p.is_alive and p.role == Role.WEREWOLF]
        good = [p for p in state.players if p.is_alive and p.role != Role.WEREWOLF]
        if not wolves:
            state.winner = "good"
        elif len(wolves) >= len(good):
            state.winner = "wolf"

    def _refresh_alive_lists(self, state: GameState) -> None:
        state.alive_players = [p.player_id for p in state.players if p.is_alive]
        state.eliminated_players = [p.player_id for p in state.players if not p.is_alive]
