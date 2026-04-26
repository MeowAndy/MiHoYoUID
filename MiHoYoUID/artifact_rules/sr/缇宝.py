from __future__ import annotations

from typing import Any, Dict, Tuple

CHARACTER_NAME = '缇宝'
BASE_WEIGHT: Dict[str, float] = {'hp': 100.0, 'atk': 0.0, 'def': 0.0, 'speed': 0.0, 'cpct': 100.0, 'cdmg': 100.0, 'stance': 0.0, 'heal': 0.0, 'recharge': 100.0, 'effPct': 0.0, 'effDef': 0.0, 'dmg': 100.0}


def get_rule(char: Dict[str, Any], context: Dict[str, Any]) -> Tuple[str, Dict[str, float]]:
    """Return the miao-plugin artifact score rule for this character."""
    return context.get('default_title') or f"{CHARACTER_NAME}-通用", dict(BASE_WEIGHT)
