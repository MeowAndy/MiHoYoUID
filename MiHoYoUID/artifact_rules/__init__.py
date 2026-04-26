from __future__ import annotations

import importlib
import re
from functools import lru_cache
from typing import Any, Callable, Dict, Tuple

RuleFunc = Callable[[Dict[str, Any], Dict[str, Any]], Tuple[str, Dict[str, float]]]


def module_name_for_character(name: str) -> str:
    return re.sub(r"[^\w\u4e00-\u9fff]+", "_", str(name), flags=re.UNICODE).strip("_") or "rule"


@lru_cache(maxsize=512)
def load_rule(game: str, name: str) -> RuleFunc | None:
    game_key = "sr" if game in {"sr", "starrail", "hkrpg"} else "gs"
    module_name = module_name_for_character(name)
    try:
        module = importlib.import_module(f"{__package__}.{game_key}.{module_name}")
    except ModuleNotFoundError:
        return None
    rule = getattr(module, "get_rule", None)
    return rule if callable(rule) else None
