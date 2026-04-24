from __future__ import annotations

import time
from typing import Dict

from gsuid_core.models import Event

from .config import MiaoConfig
from .database import MiaoUserHistory


def is_admin_event(ev: Event) -> bool:
    """兼容不同适配器字段的管理员判断。"""
    return bool(
        getattr(ev, "is_master", False)
        or getattr(ev, "isMaster", False)
        or getattr(ev, "is_admin", False)
        or getattr(ev, "isAdmin", False)
        or getattr(ev, "is_owner", False)
        or getattr(ev, "isOwner", False)
    )


def can_use_plugin(ev: Event) -> bool:
    allow_guest = MiaoConfig.get_config("AllowGuestUse").data
    if allow_guest:
        return True
    return is_admin_event(ev)


async def add_history(ev: Event, action: str, detail: str) -> None:
    """写入历史记录（失败不抛异常，避免影响主流程）。"""
    try:
        await MiaoUserHistory.insert_data(
            user_id=ev.user_id,
            bot_id=ev.bot_id,
            action=action,
            detail=detail,
            ts=int(time.time()),
        )
    except Exception:
        return


async def get_recent_history_lines(ev: Event) -> list[str]:
    """读取最近历史并格式化。"""
    limit = MiaoConfig.get_config("RecentHistoryLimit").data
    try:
        rows = await MiaoUserHistory.get_all_data()
    except Exception:
        return []

    rows = [
        x for x in rows
        if getattr(x, "user_id", "") == ev.user_id and getattr(x, "bot_id", "") == ev.bot_id
    ]
    rows.sort(key=lambda x: getattr(x, "ts", 0), reverse=True)
    out = []
    for r in rows[:limit]:
        out.append(f"- {getattr(r, 'action', '')}: {getattr(r, 'detail', '')}")
    return out
