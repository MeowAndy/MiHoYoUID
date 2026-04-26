from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from .alias_data import resolve_alias

MIAO_ROOT = Path(r"E:\gsuid_core\gsuid_core\plugins\miao-plugin\resources")


def _game_key(game: str = "gs") -> str:
    return "sr" if game in {"sr", "starrail", "hkrpg"} else "gs"


def _char_dir(game: str = "gs") -> Path:
    return MIAO_ROOT / ("meta-sr" if _game_key(game) == "sr" else "meta-gs") / "character"


def _clean(text: Any) -> str:
    text = unescape(str(text or ""))
    text = re.sub(r"<nobr>|</nobr>|<span>|</span>", "", text)
    text = re.sub(r"<h3>(.*?)</h3>", r"【\1】", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\$\d+\[[^\]]+\]", "倍率", text)
    return text.replace("\n", " ").strip()


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _char_data(name: str, game: str = "gs") -> Dict[str, Any]:
    game = _game_key(game)
    name = (resolve_alias(name, game=game) or name or "").strip()
    if not name:
        return {}
    direct = _char_dir(game) / name / "data.json"
    if direct.exists():
        return _load_json(direct)
    for item in _char_dir(game).iterdir():
        if item.is_dir() and (name in item.name or item.name in name):
            data = _load_json(item / "data.json")
            if data:
                return data
    return {}


def get_char_wiki_data(name: str, game: str = "gs") -> Dict[str, Any]:
    return _char_data(name, game)


def _fmt_materials(materials: Any) -> List[str]:
    if not isinstance(materials, dict):
        return []
    labels = {
        "gem": "突破宝石",
        "boss": "首领材料",
        "specialty": "区域特产",
        "normal": "常规材料",
        "talent": "天赋书",
        "weekly": "周本材料",
        "weapon": "命途材料",
    }
    return [f"{labels.get(k, k)}：{v}" for k, v in materials.items() if v]


def _iter_talents(data: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    talents = data.get("talent") or {}
    if isinstance(talents, dict):
        for key in ("a", "e", "q", "t", "z", "q2"):
            val = talents.get(key)
            if isinstance(val, dict):
                yield val
        for val in talents.values():
            if isinstance(val, dict) and val.get("name") not in {t.get("name") for t in []}:
                yield val


def _talent_lines(data: Dict[str, Any], limit: int = 4) -> List[str]:
    lines: List[str] = []
    seen = set()
    for talent in _iter_talents(data):
        name = str(talent.get("name") or talent.get("type") or "技能")
        if name in seen:
            continue
        seen.add(name)
        typ = str(talent.get("type") or "")
        desc = talent.get("desc")
        if isinstance(desc, list):
            desc_text = " ".join(_clean(x) for x in desc[:3])
        else:
            desc_text = _clean(desc)
        lines.append(f"{typ + ' · ' if typ else ''}{name}：{desc_text[:120]}")
        if len(lines) >= limit:
            break
    return lines


def _cons_lines(data: Dict[str, Any], limit: int = 6) -> List[str]:
    cons = data.get("cons") or data.get("constellation") or data.get("rank") or {}
    if isinstance(cons, list):
        items = cons
    elif isinstance(cons, dict):
        items = list(cons.values())
    else:
        items = []
    lines: List[str] = []
    for idx, item in enumerate(items[:limit], start=1):
        if isinstance(item, dict):
            name = item.get("name") or f"第{idx}层"
            desc = _clean(item.get("desc") or item.get("effect"))
        else:
            name, desc = f"第{idx}层", _clean(item)
        lines.append(f"{idx}. {name}：{desc[:110]}")
    return lines


def wiki_image_payload(name: str, mode: str = "wiki", game: str = "gs") -> Tuple[Dict[str, Any], str, str]:
    game = _game_key(game)
    data = _char_data(name, game)
    return data, mode, game


def render_char_wiki_text(name: str, mode: str = "wiki", game: str = "gs") -> str:
    game = _game_key(game)
    data = _char_data(name, game)
    prefix = "【喵喵崩铁资料】" if game == "sr" else "【喵喵原神资料】"
    if not data:
        return f"{prefix}\n未找到 {name} 的 miao-plugin 资料。"
    title = str(data.get("name") or name)
    lines = [prefix, f"{title} · {data.get('title') or data.get('allegiance') or ''}".strip()]
    if mode in {"material", "材料", "素材", "养成"}:
        lines.append("养成材料：")
        lines.extend(_fmt_materials(data.get("materials")) or ["暂无材料数据"])
        return "\n".join(lines)
    if mode in {"talent", "天赋", "技能", "行迹"}:
        lines.append("技能/行迹：")
        lines.extend(_talent_lines(data, limit=6) or ["暂无技能数据"])
        return "\n".join(lines)
    if mode in {"cons", "命座", "命之座", "星魂"}:
        lines.append("命座/星魂：")
        lines.extend(_cons_lines(data) or ["暂无命座/星魂数据"])
        return "\n".join(lines)
    lines.extend([
        f"星级：{data.get('star') or '-'} · 元素/属性：{data.get('elem') or '-'} · 武器/命途：{data.get('weapon') or '-'}",
        f"阵营：{data.get('allegiance') or '-'} · 生日：{data.get('birth') or '-'}",
        f"中文CV：{data.get('cncv') or '-'} · 日文CV：{data.get('jpcv') or '-'}",
        f"简介：{_clean(data.get('desc'))}",
        "养成材料：" + "；".join(_fmt_materials(data.get("materials"))[:4]),
    ])
    return "\n".join(lines)