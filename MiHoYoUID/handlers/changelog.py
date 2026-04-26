from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.segment import MessageSegment
from gsuid_core.sv import SV

from ..auth import can_use_plugin
from ..config import MiaoConfig
from ..version import GENSHIN_CHANGELOGS, STAR_RAIL_CHANGELOGS

sv_changelog = SV("GsCoreMiao更新日志")


def _format_logs(logs):
    msg_list = []
    for item in logs:
        content = f"{item['version']} ({item['date']})"
        for x in item.get("items", []):
            content += f"\n• {x}"
        msg_list.append(content)
    return MessageSegment.node(msg_list)


@sv_changelog.on_fullmatch(("原神更新日志", "原神changelog"), block=True)
async def send_genshin_changelog(bot: Bot, ev: Event):
    if not can_use_plugin(ev):
        return await bot.send("当前配置禁止游客使用，仅管理员可调用该指令")

    limit = MiaoConfig.get_config("UpdateLogLimit").data
    logs = GENSHIN_CHANGELOGS[:limit]
    await bot.send(_format_logs(logs))


@sv_changelog.on_fullmatch(("崩铁更新日志", "崩铁changelog", "星铁更新日志", "星铁changelog"), block=True)
async def send_starrail_changelog(bot: Bot, ev: Event):
    if not can_use_plugin(ev):
        return await bot.send("当前配置禁止游客使用，仅管理员可调用该指令")

    limit = MiaoConfig.get_config("UpdateLogLimit").data
    logs = STAR_RAIL_CHANGELOGS[:limit]
    await bot.send(_format_logs(logs))
