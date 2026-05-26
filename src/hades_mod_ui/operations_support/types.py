from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ArcanaEditorPayload:
    enabled: bool
    effect_multipliers: dict[str, str]
    unlock_upgrade_cost_multiplier: str
    starting_grasp_limit: str
    grasp_growth_multiplier: str


@dataclass(frozen=True)
class InitialStatsPayload:
    enabled: bool
    max_health: str
    max_mana: str
    starting_money: str


ProfilePayload = dict[str, Any]

__all__ = ["ArcanaEditorPayload", "InitialStatsPayload", "ProfilePayload"]
