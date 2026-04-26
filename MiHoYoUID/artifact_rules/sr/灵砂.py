from __future__ import annotations

from typing import Any, Dict, Tuple

CHARACTER_NAME = '灵砂'
BASE_WEIGHT: Dict[str, float] = {'hp': 0.0, 'atk': 75.0, 'def': 0.0, 'speed': 100.0, 'cpct': 0.0, 'cdmg': 0.0, 'stance': 100.0, 'heal': 100.0, 'recharge': 100.0, 'effPct': 0.0, 'effDef': 0.0, 'dmg': 0.0}


def get_rule(char: Dict[str, Any], context: Dict[str, Any]) -> Tuple[str, Dict[str, float]]:
    """Return the miao-plugin artifact score rule for this character."""
    return context.get('default_title') or f"{CHARACTER_NAME}-通用", dict(BASE_WEIGHT)
