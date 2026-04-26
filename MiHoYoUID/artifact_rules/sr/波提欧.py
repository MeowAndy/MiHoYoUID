from __future__ import annotations

from typing import Any, Dict, Tuple

CHARACTER_NAME = '波提欧'
BASE_WEIGHT: Dict[str, float] = {'hp': 50.0, 'atk': 50.0, 'def': 50.0, 'speed': 100.0, 'cpct': 50.0, 'cdmg': 50.0, 'stance': 100.0, 'heal': 0.0, 'recharge': 50.0, 'effPct': 0.0, 'effDef': 0.0, 'dmg': 50.0}


def get_rule(char: Dict[str, Any], context: Dict[str, Any]) -> Tuple[str, Dict[str, float]]:
    """Return the miao-plugin artifact score rule for this character."""
    return context.get('default_title') or f"{CHARACTER_NAME}-通用", dict(BASE_WEIGHT)
