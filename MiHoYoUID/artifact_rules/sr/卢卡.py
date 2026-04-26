from __future__ import annotations

from typing import Any, Dict, Tuple

CHARACTER_NAME = '卢卡'
BASE_WEIGHT: Dict[str, float] = {'hp': 0.0, 'atk': 100.0, 'def': 0.0, 'speed': 100.0, 'cpct': 0.0, 'cdmg': 0.0, 'stance': 75.0, 'heal': 0.0, 'recharge': 50.0, 'effPct': 75.0, 'effDef': 0.0, 'dmg': 100.0}


def get_rule(char: Dict[str, Any], context: Dict[str, Any]) -> Tuple[str, Dict[str, float]]:
    """Return the miao-plugin artifact score rule for this character."""
    return context.get('default_title') or f"{CHARACTER_NAME}-通用", dict(BASE_WEIGHT)
