from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

EffectValues = Tuple[float, float, float, float, float]

_PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_MIAO_WEAPON_DIRS = (
    _PLUGIN_ROOT / "resources" / "meta-sr" / "weapon",
    _PLUGIN_ROOT.parent / "miao-plugin" / "resources" / "meta-sr" / "weapon",
    Path("E:/gsuid_core/gsuid_core/plugins/miao-plugin/resources/meta-sr/weapon"),
)
_EFFECT_KEYS = ("skill", "desc", "description", "effect", "effect_desc", "skill_desc", "passive", "weapon_effect")


def _step(start: float, step: float | None = None) -> EffectValues:
    if step is None:
        step = start / 4
    return tuple(start + step * idx for idx in range(5))  # type: ignore[return-value]


def _fmt_num(value: Any) -> str:
    try:
        num = float(value)
    except (TypeError, ValueError):
        return str(value)
    if abs(num - round(num)) < 0.01:
        return str(int(round(num)))
    return f"{num:.1f}".rstrip("0").rstrip(".")


def _norm_name(name: str) -> str:
    return re.sub(r"[\s·•・,，。.!！?？:：;；'‘’\"“”【】\[\]（）()《》<>「」-]", "", str(name or "")).lower()


def _pick(values: Iterable[Any], refine: int) -> Any:
    arr = list(values)
    if not arr:
        return ""
    idx = max(1, min(int(refine or 1), 5)) - 1
    return arr[min(idx, len(arr) - 1)]


def _render(template: str, values: Dict[str, Iterable[Any]], refine: int) -> str:
    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in values:
            return match.group(0)
        return _fmt_num(_pick(values[key], refine))

    return re.sub(r"\{([A-Za-z0-9_]+)\}", repl, template)


def _clean_text(text: Any) -> str:
    text = str(text or "").strip()
    if not text:
        return ""
    text = re.sub(r"<br\s*/?>", "。", text, flags=re.IGNORECASE)
    text = re.sub(r"<nobr>\s*([^<]*?)\s*</nobr>", r"\1", text, flags=re.IGNORECASE)
    text = re.sub(r"<color=[^>]*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"</color>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\r", "").replace("\n", "。")
    text = re.sub(r"。{2,}", "。", text)
    return text.strip("。；; ")


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


@lru_cache(maxsize=1)
def _miao_alias_index() -> Dict[str, str]:
    index: Dict[str, str] = {}
    for weapon_dir in _MIAO_WEAPON_DIRS:
        alias_file = weapon_dir / "alias.js"
        if not alias_file.exists():
            continue
        try:
            content = alias_file.read_text(encoding="utf-8")
        except Exception:
            continue
        for block in re.finditer(r"([\u4e00-\u9fa5A-Za-z0-9·，,！!]+)\s*:\s*\[([^\]]*)\]", content):
            canonical = block.group(1).strip().strip("'\"")
            index[_norm_name(canonical)] = canonical
            for alias in re.findall(r"['\"]([^'\"]+)['\"]", block.group(2)):
                index[_norm_name(alias)] = canonical
    return index


@lru_cache(maxsize=1)
def _miao_weapon_files() -> Dict[str, Path]:
    files: Dict[str, Path] = {}
    for weapon_dir in _MIAO_WEAPON_DIRS:
        if not weapon_dir.exists():
            continue
        for data_file in weapon_dir.rglob("data.json"):
            data = _load_json(data_file)
            name = str(data.get("name") or data_file.parent.name).strip()
            if name and name != "weapon":
                files.setdefault(_norm_name(name), data_file)
        data_file = weapon_dir / "data.json"
        data = _load_json(data_file)
        for item in data.values():
            if isinstance(item, dict):
                name = str(item.get("name") or item.get("sName") or "").strip()
                if name:
                    detail = weapon_dir / str(item.get("type") or "") / name / "data.json"
                    if detail.exists():
                        files.setdefault(_norm_name(name), detail)
    for alias, canonical in _miao_alias_index().items():
        path = files.get(_norm_name(canonical))
        if path:
            files.setdefault(alias, path)
    return files


def _extract_effect_text(value: Any, refine: int) -> str:
    if isinstance(value, dict):
        skill = value.get("skill") if isinstance(value.get("skill"), dict) else value
        desc = str(skill.get("desc") or skill.get("description") or skill.get("skill_desc") or "")
        tables = skill.get("tables") if isinstance(skill.get("tables"), dict) else {}
        if desc and tables:
            def repl(match: re.Match[str]) -> str:
                idx = match.group(1)
                values = tables.get(idx) or tables.get(str(idx)) or []
                return _fmt_num(_pick(values, refine))

            desc = re.sub(r"\$([0-9]+)(?:\[[^\]]*\])?", repl, desc)
            return _clean_text(desc)
        for key in _EFFECT_KEYS:
            text = _extract_effect_text(value.get(key), refine)
            if text:
                return text
        return ""
    if isinstance(value, list):
        return "。".join(filter(None, (_extract_effect_text(item, refine) for item in value)))
    return _clean_text(value)


@lru_cache(maxsize=1024)
def _miao_detail_effect(norm_name: str, refine: int) -> str:
    data_file = _miao_weapon_files().get(norm_name)
    if not data_file:
        return ""
    data = _load_json(data_file)
    return _extract_effect_text(data, refine)


# 内置兜底：当本地/外部 miao-plugin 资源不存在时仍可显示常用光锥效果。
LIGHT_CONE_EFFECTS: Dict[str, Dict[str, Any]] = {
    "行于流逝的岸": {
        "template": "暴击伤害提高{cdmg}%；使敌方陷入泡影后，装备者造成的伤害提高{dmg}%，终结技伤害额外提高{qDmg}%。",
        "values": {"cdmg": _step(36), "dmg": _step(24), "qDmg": _step(24)},
        "aliases": ("行于流逝", "流逝的岸", "黄泉专武"),
    },
    "晚安与睡颜": {
        "template": "敌方目标每承受1个负面状态，装备者对其造成的伤害提高{dmg}%，最多叠加3层。",
        "values": {"dmg": _step(12)},
        "aliases": ("晚安", "睡颜"),
    },
    "让告别，更美一些": {
        "template": "使装备者的生命上限提高{hpPct}%，装备者或装备者的忆灵在自身回合内损失生命值时，装备者获得【冥花】，【冥花】可以使装备者和装备者的忆灵造成伤害时，无视目标{ignore}%的防御力，持续2回合。当装备者的忆灵消失时，使装备者行动提前{advance}%。该效果最多触发1次，装备者每次施放终结技时重置触发次数。",
        "values": {"hpPct": _step(30, 7.5), "ignore": _step(30, 5), "advance": _step(12, 3)},
        "aliases": ("让告别更美一些", "遐蝶专武"),
    },
}

_INDEX: Dict[str, str] = {}
for _name, _data in LIGHT_CONE_EFFECTS.items():
    _INDEX[_norm_name(_name)] = _name
    for _alias in _data.get("aliases", ()):
        _INDEX[_norm_name(str(_alias))] = _name


def get_light_cone_effect(name: str, refine: int = 1) -> str:
    """返回星铁光锥详细效果，优先读取 miao-plugin data.json 的 skill.desc 与 tables。"""
    norm_name = _norm_name(name)
    effect = _miao_detail_effect(norm_name, max(1, min(int(refine or 1), 5)))
    if effect:
        return effect
    key = _INDEX.get(norm_name)
    if not key:
        return ""
    data = LIGHT_CONE_EFFECTS[key]
    return _render(str(data.get("template") or ""), data.get("values") or {}, refine)
