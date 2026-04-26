import asyncio
import json
import time
from pathlib import Path
from typing import Any, Dict

from .path import MAIN_PATH

_USER_CFG_PATH = MAIN_PATH / "user_config.json"
_LOCK = asyncio.Lock()


def _load_json() -> Dict[str, Any]:
    if not _USER_CFG_PATH.exists():
        return {}
    try:
        return json.loads(_USER_CFG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_json(data: Dict[str, Any]) -> None:
    _USER_CFG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _USER_CFG_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _user_key(user_id: str, bot_id: str) -> str:
    return f"{bot_id}:{user_id}"


def _uid_history(default_uid: str, roles: list[dict[str, Any]]) -> list[str]:
    values = [default_uid]
    values.extend(str(x.get("game_uid") or x.get("uid") or "") for x in roles if isinstance(x, dict))
    return [x for x in dict.fromkeys(values) if x][:10]


async def get_group_bot_self_id(group_id: str) -> str:
    if not group_id:
        return ""
    async with _LOCK:
        data = _load_json()
        return str(data.get("_sign_group_bots", {}).get(str(group_id), ""))


async def set_group_bot_self_id(group_id: str, bot_self_id: str) -> None:
    if not group_id or not bot_self_id:
        return
    async with _LOCK:
        data = _load_json()
        group_bots = data.get("_sign_group_bots")
        if not isinstance(group_bots, dict):
            group_bots = {}
        group_bots[str(group_id)] = str(bot_self_id)
        data["_sign_group_bots"] = group_bots
        _save_json(data)


async def get_user_cfg(user_id: str, bot_id: str) -> Dict[str, Any]:
    async with _LOCK:
        data = _load_json()
        return data.get(_user_key(user_id, bot_id), {})


async def set_user_cfg(user_id: str, bot_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
    async with _LOCK:
        data = _load_json()
        k = _user_key(user_id, bot_id)
        old = data.get(k, {})
        merged = {**old, **patch, "updated_at": int(time.time())}
        data[k] = merged
        _save_json(data)
        return merged


async def get_all_user_cfg() -> Dict[str, Any]:
    async with _LOCK:
        return _load_json()


async def set_rank_record(group_id: str, game: str, char_name: str, uid: str, record: Dict[str, Any]) -> None:
    async with _LOCK:
        data = _load_json()
        ranks = data.get("_group_ranks")
        if not isinstance(ranks, dict):
            ranks = {}
        group_map = ranks.setdefault(str(group_id), {})
        game_map = group_map.setdefault(str(game), {})
        char_map = game_map.setdefault(str(char_name), {})
        char_map[str(uid)] = record
        data["_group_ranks"] = ranks
        _save_json(data)


async def get_all_rank_records(group_id: str, game: str) -> Dict[str, Any]:
    async with _LOCK:
        data = _load_json()
        ranks = data.get("_group_ranks") or {}
        if not isinstance(ranks, dict):
            return {}
        group_map = ranks.get(str(group_id)) or {}
        if not isinstance(group_map, dict):
            return {}
        game_map = group_map.get(str(game)) or {}
        return game_map if isinstance(game_map, dict) else {}


async def reset_rank_records(group_id: str, game: str, char_name: str = "") -> int:
    async with _LOCK:
        data = _load_json()
        ranks = data.get("_group_ranks") or {}
        if not isinstance(ranks, dict):
            return 0
        group_map = ranks.get(str(group_id)) or {}
        if not isinstance(group_map, dict):
            return 0
        game_map = group_map.get(str(game)) or {}
        if not isinstance(game_map, dict):
            return 0
        if char_name:
            removed = len(game_map.get(str(char_name), {}) or {})
            game_map.pop(str(char_name), None)
        else:
            removed = sum(len(v or {}) for v in game_map.values() if isinstance(v, dict))
            group_map[str(game)] = {}
        data["_group_ranks"] = ranks
        _save_json(data)
        return removed


async def reset_user_cfg(user_id: str, bot_id: str) -> None:
    async with _LOCK:
        data = _load_json()
        k = _user_key(user_id, bot_id)
        if k in data:
            del data[k]
            _save_json(data)


async def bind_uid(user_id: str, bot_id: str, uid: str, game: str = "gs") -> Dict[str, Any]:
    key = "sr_uid" if game in {"sr", "starrail", "hkrpg"} else "uid"
    list_key = "sr_uid_list" if game in {"sr", "starrail", "hkrpg"} else "uid_list"
    async with _LOCK:
        data = _load_json()
        k = _user_key(user_id, bot_id)
        old = data.get(k, {})
        uid_list = old.get(list_key) if isinstance(old.get(list_key), list) else []
        uid_list = [str(x) for x in uid_list if str(x).strip()]
        if uid not in uid_list:
            uid_list.append(uid)
        merged = {**old, key: uid, list_key: uid_list[-10:], "updated_at": int(time.time())}
        data[k] = merged
        _save_json(data)
        return merged


async def bind_mys_cookie(
    user_id: str,
    bot_id: str,
    cookie: str,
    roles: list[dict[str, Any]],
    sr_roles: list[dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    sr_roles = sr_roles or []
    default_role = roles[0] if roles else {}
    default_sr_role = sr_roles[0] if sr_roles else {}
    default_uid = str(default_role.get("game_uid") or default_role.get("uid") or "") if default_role else ""
    default_sr_uid = str(default_sr_role.get("game_uid") or default_sr_role.get("uid") or "") if default_sr_role else ""
    patch: Dict[str, Any] = {
        "mys_cookie": cookie,
        "mys_roles": roles,
        "mys_sr_roles": sr_roles,
        "login_type": "mys_cookie",
        "login_at": int(time.time()),
    }
    if default_uid:
        patch["uid"] = default_uid
        patch["uid_list"] = _uid_history(default_uid, roles)
    if default_sr_uid:
        patch["sr_uid"] = default_sr_uid
        patch["sr_uid_list"] = _uid_history(default_sr_uid, sr_roles)
    return await set_user_cfg(user_id, bot_id, patch)


async def unbind_mys_cookie(user_id: str, bot_id: str) -> Dict[str, Any]:
    async with _LOCK:
        data = _load_json()
        k = _user_key(user_id, bot_id)
        old = data.get(k, {})
        merged = {**old, "updated_at": int(time.time())}
        for key in ("mys_cookie", "mys_roles", "mys_sr_roles", "login_type", "login_at"):
            merged.pop(key, None)
        data[k] = merged
        _save_json(data)
        return merged


async def unbind_uid(user_id: str, bot_id: str, game: str = "gs") -> Dict[str, Any]:
    async with _LOCK:
        data = _load_json()
        k = _user_key(user_id, bot_id)
        old = data.get(k, {})
        merged = {**old, "updated_at": int(time.time())}
        is_sr = game in {"sr", "starrail", "hkrpg"}
        merged.pop("sr_uid" if is_sr else "uid", None)
        merged.pop("sr_uid_list" if is_sr else "uid_list", None)
        data[k] = merged
        _save_json(data)
        return merged
