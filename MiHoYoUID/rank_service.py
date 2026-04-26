from __future__ import annotations

import time
from typing import Any, Dict, Iterable, List, Tuple

from .alias_data import resolve_alias
from .artifact_service import artifact_rank, character_artifact_score
from .damage_service import estimate_character_damage
from .panel_models import PanelResult
from .panel_renderer import CHARACTER_ID_NAMES
from .store import get_all_rank_records, reset_rank_records, set_rank_record


def _game_key(game: str = "gs") -> str:
    return "sr" if game in {"sr", "starrail", "hkrpg"} else "gs"


def _char_name(char: Dict[str, Any]) -> str:
    name = str(char.get("name") or char.get("avatar_name") or "").strip()
    if name and not name.isdigit():
        return name
    avatar_id = char.get("avatar_id") or char.get("avatarId")
    try:
        mapped = CHARACTER_ID_NAMES.get(int(avatar_id))
    except (TypeError, ValueError):
        mapped = None
    return mapped or f"角色ID {avatar_id or '?'}"


def _char_key(char: Dict[str, Any], game: str = "gs") -> str:
    name = _char_name(char)
    resolved = resolve_alias(name, game=game) or name
    return resolved.strip()


def _char_match(char: Dict[str, Any], query: str, game: str = "gs") -> bool:
    if not query:
        return True
    q = query.strip().lower()
    resolved = (resolve_alias(query, game=game) or query).strip().lower()
    parts = [
        _char_name(char),
        str(char.get("name") or ""),
        str(char.get("avatar_name") or ""),
        str(char.get("avatar_id") or char.get("avatarId") or ""),
    ]
    text = " ".join(parts).lower()
    return q in text or resolved in text


def _char_score_payload(char: Dict[str, Any]) -> Dict[str, Any]:
    total, scores, rule = character_artifact_score(char)
    dmg = estimate_character_damage(char)
    props = char.get("fight_props") or {}
    crit = float(props.get("暴击率") or props.get("cpct") or props.get("crit_rate") or 0)
    cdmg = float(props.get("暴击伤害") or props.get("cdmg") or props.get("crit_dmg") or 0)
    valid = round(sum(s for s in scores if s > 0), 1)
    return {
        "artifact_score": total,
        "artifact_scores": scores,
        "artifact_rule": rule,
        "artifact_rank": artifact_rank(total / 6 if char.get("game") == "sr" and total else total),
        "damage_expect": float(dmg.get("expect") or 0),
        "crit_score": round(crit * 2 + cdmg, 1),
        "valid_score": valid,
    }


def rank_metric_title(mode: str, game: str = "gs") -> str:
    is_sr = _game_key(game) == "sr"
    return {
        "mark": "遗器评分" if is_sr else "圣遗物评分",
        "valid": "有效词条",
        "crit": "双爆词条",
        "dmg": "伤害期望",
    }.get(mode, "伤害期望")


def _metric_value(record: Dict[str, Any], mode: str) -> float:
    key = {
        "mark": "artifact_score",
        "valid": "valid_score",
        "crit": "crit_score",
        "dmg": "damage_expect",
    }.get(mode, "damage_expect")
    try:
        return float(record.get(key) or 0)
    except (TypeError, ValueError):
        return 0.0


async def update_group_rank_records(result: PanelResult, group_id: str, user_id: str = "") -> int:
    if not group_id:
        return 0
    game = _game_key(result.game)
    count = 0
    for char in result.characters or []:
        if not isinstance(char, dict):
            continue
        item = dict(char)
        item.setdefault("game", game)
        payload = _char_score_payload(item)
        record = {
            **payload,
            "uid": result.uid,
            "user_id": str(user_id or ""),
            "group_id": str(group_id),
            "game": game,
            "char_name": _char_key(item, game),
            "level": item.get("level"),
            "constellation": item.get("constellation"),
            "source": result.source,
            "updated_at": int(time.time()),
        }
        await set_rank_record(str(group_id), game, record["char_name"], result.uid, record)
        count += 1
    return count


async def reset_group_rank(group_id: str, game: str = "gs", char_name: str = "") -> int:
    return await reset_rank_records(str(group_id), _game_key(game), char_name)


async def get_rank_rows(group_id: str, game: str = "gs", char_name: str = "", mode: str = "dmg", limit: int = 20) -> List[Dict[str, Any]]:
    data = await get_all_rank_records(str(group_id), _game_key(game))
    rows: List[Dict[str, Any]] = []
    resolved = resolve_alias(char_name, game=game) or char_name
    for name, uid_map in data.items():
        if resolved and name != resolved:
            continue
        if not isinstance(uid_map, dict):
            continue
        for record in uid_map.values():
            if isinstance(record, dict):
                rows.append(record)
    rows.sort(key=lambda r: _metric_value(r, mode), reverse=True)
    return rows[:limit]


def format_rank_list(rows: Iterable[Dict[str, Any]], group_id: str, game: str = "gs", char_name: str = "", mode: str = "dmg") -> str:
    rows = list(rows)
    title_name = char_name or "全角色"
    title = rank_metric_title(mode, game)
    prefix = "【喵喵崩铁排名】" if _game_key(game) == "sr" else "【喵喵原神排名】"
    lines = [prefix, f"群：{group_id} · {title_name} · {title}"]
    if not rows:
        lines.append("暂无排名：请先在本群使用面板/更新面板命令，让插件记录可排名数据。")
        return "\n".join(lines)
    for idx, row in enumerate(rows, start=1):
        metric = _metric_value(row, mode)
        uid = str(row.get("uid") or "-")
        name = str(row.get("char_name") or title_name)
        cons = row.get("constellation")
        lv = row.get("level") or "?"
        extra = f"C{cons}" if cons is not None else ""
        lines.append(f"{idx}. {name} Lv.{lv} {extra} · UID {uid} · {metric:.1f}")
    return "\n".join(lines)


def format_rank_detail(row: Dict[str, Any] | None, group_id: str, game: str = "gs", char_name: str = "", mode: str = "dmg") -> str:
    if not row:
        return format_rank_list([], group_id, game, char_name, mode)
    title = rank_metric_title(mode, game)
    prefix = "【喵喵崩铁群内最强】" if _game_key(game) == "sr" else "【喵喵原神群内最强】"
    lines = [prefix, f"群：{group_id} · {row.get('char_name') or char_name} · {title}"]
    lines.append(f"UID：{row.get('uid')}  Lv.{row.get('level') or '?'}  C{row.get('constellation') if row.get('constellation') is not None else '-'}")
    lines.append(f"{title}：{_metric_value(row, mode):.1f}")
    lines.append(f"遗器/圣遗物：{row.get('artifact_score') or 0:.1f} [{row.get('artifact_rank') or '-'}]")
    lines.append(f"伤害期望：{row.get('damage_expect') or 0:.0f}")
    lines.append(f"双爆词条：{row.get('crit_score') or 0:.1f} · 有效词条：{row.get('valid_score') or 0:.1f}")
    lines.append(f"规则：{row.get('artifact_rule') or '通用'}")
    return "\n".join(lines)


def training_score(char: Dict[str, Any]) -> float:
    item = dict(char)
    payload = _char_score_payload(item)
    level = float(item.get("level") or 1)
    skills = [float(x or 0) for x in item.get("skill_levels") or []]
    skill_score = sum(skills[:5]) / max(len(skills[:5]) or 1, 1) * 4
    artifact_score = min(float(payload.get("artifact_score") or 0) / (6 if item.get("game") == "sr" else 5), 66)
    cons = float(item.get("constellation") or 0)
    return round(min(level, 90) / 90 * 25 + skill_score + artifact_score + cons * 1.5, 1)


def render_training_stat_text(result: PanelResult) -> str:
    chars = [dict(c, game=result.game) for c in result.characters or [] if isinstance(c, dict)]
    is_sr = _game_key(result.game) == "sr"
    title = "【喵喵崩铁练度统计】" if is_sr else "【喵喵原神练度统计】"
    lines = [title, f"UID：{result.uid} · 数据源：{result.source}"]
    if not chars:
        lines.append("当前数据源没有返回可统计的角色详情。")
        return "\n".join(lines)
    rows: List[Tuple[float, Dict[str, Any]]] = sorted(((training_score(c), c) for c in chars), key=lambda x: x[0], reverse=True)
    avg = sum(score for score, _ in rows) / len(rows)
    lines.append(f"角色数：{len(rows)} · 平均练度：{avg:.1f}")
    for idx, (score, char) in enumerate(rows[:12], start=1):
        total, _, rule = character_artifact_score(char)
        skills = "/".join(str(x) for x in char.get("skill_levels") or []) or "-"
        lines.append(f"{idx}. {_char_name(char)} Lv.{char.get('level') or '?'} C{char.get('constellation') or 0} · 练度 {score:.1f} · {'遗器' if is_sr else '圣遗物'} {total:.1f} · {'行迹' if is_sr else '天赋'} {skills}")
        lines.append(f"   规则：{rule}")
    return "\n".join(lines)