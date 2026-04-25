from __future__ import annotations

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..auth import can_use_plugin
from ..calendar_service import fetch_calendar
from ..panel_renderer import render_calendar_image

sv_calendar = SV("GsCoreMiao活动日历")


async def _send_calendar(bot: Bot, ev: Event, game: str, list_mode: bool) -> None:
    if not can_use_plugin(ev):
        return await bot.send("当前配置禁止游客使用，仅管理员可调用该指令")
    try:
        data = await fetch_calendar(game, list_mode=list_mode)
        await bot.send(await render_calendar_image(data))
    except Exception as e:
        name = "原神" if game == "gs" else "崩铁"
        await bot.send(f"{name}日历获取失败：{e}")


@sv_calendar.on_regex(r"^(崩铁|星铁)(日历|日历列表|活动)$", block=True)
async def send_starrail_calendar(bot: Bot, ev: Event):
    text = getattr(ev, "raw_text", "") or ""
    await _send_calendar(bot, ev, "sr", "列表" in text or text.endswith("活动"))


@sv_calendar.on_regex(r"^原神(日历|日历列表|活动)$", block=True)
async def send_genshin_calendar(bot: Bot, ev: Event):
    text = getattr(ev, "raw_text", "") or ""
    await _send_calendar(bot, ev, "gs", "列表" in text or text.endswith("活动"))
