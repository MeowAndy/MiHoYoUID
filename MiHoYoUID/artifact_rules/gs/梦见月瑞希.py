from __future__ import annotations

from typing import Any, Dict, Tuple

CHARACTER_NAME = '梦见月瑞希'
BASE_WEIGHT: Dict[str, float] = {'hp': 0.0, 'atk': 30.0, 'def': 0.0, 'cpct': 30.0, 'cdmg': 30.0, 'mastery': 100.0, 'dmg': 80.0, 'phy': 0.0, 'recharge': 45.0, 'heal': 95.0}


def get_rule(char: Dict[str, Any], context: Dict[str, Any]) -> Tuple[str, Dict[str, float]]:
    """Return the miao-plugin artifact score rule for this character."""
    return context.get('default_title') or f"{CHARACTER_NAME}-通用", dict(BASE_WEIGHT)
