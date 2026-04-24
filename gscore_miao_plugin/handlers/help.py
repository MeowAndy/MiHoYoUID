from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..auth import can_use_plugin
from ..config import MiaoConfig
from ..help_data import HELP_GROUPS
from ..version import PLUGIN_VERSION

sv_help = SV("GsCoreMiao帮助")


@sv_help.on_fullmatch(("帮助", "菜单"), block=True)
async def send_help(bot: Bot, ev: Event):
    if not MiaoConfig.get_config("EnableHelp").data:
        return
    if not can_use_plugin(ev):
        return await bot.send("当前配置禁止游客使用，仅管理员可调用该指令")

    title = MiaoConfig.get_config("HelpTitle").data
    subtitle = MiaoConfig.get_config("HelpSubTitle").data
    setting_export = MiaoConfig.get_config("EnableSettingExport").data
    setting_reset = MiaoConfig.get_config("EnableSettingReset").data

    lines = [f"{title}", f"{subtitle}", ""]
    idx = 1
    for group in HELP_GROUPS:
        lines.append(f"【{group['group']}】")
        for item in group["items"]:
            cmd = item["cmd"]
            if (not setting_export) and ("设置导出" in cmd):
                continue
            if (not setting_reset) and ("设置重置" in cmd):
                continue
            lines.append(f"{idx}) {cmd} - {item['desc']}")
            idx += 1
        lines.append("")
    msg = "\n".join(lines).strip()
    await bot.send(msg)


@sv_help.on_fullmatch(("版本",), block=True)
async def send_version(bot: Bot, ev: Event):
    if not MiaoConfig.get_config("EnableVersion").data:
        return
    if not can_use_plugin(ev):
        return await bot.send("当前配置禁止游客使用，仅管理员可调用该指令")
    await bot.send(f"gscore_miao-plugin v{PLUGIN_VERSION}")


@sv_help.on_fullmatch(("面板", "角色面板", "角色卡片"), block=True)
async def send_panel_notice(bot: Bot, ev: Event):
    if not can_use_plugin(ev):
        return await bot.send("当前配置禁止游客使用，仅管理员可调用该指令")
    await bot.send(
        "角色面板查询已保留命令入口。\n"
        "GsCore 版当前完成设置、帮助、版本与基础权限迁移；"
        "面板数据查询需接入米游社/Enka/Miao 等数据源后启用。"
    )
