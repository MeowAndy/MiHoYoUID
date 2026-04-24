from typing import Dict

from gsuid_core.utils.plugins_config.models import (
    GSC,
    GsBoolConfig,
    GsIntConfig,
    GsListStrConfig,
    GsStrConfig,
)

CONFIG_DEFAULT: Dict[str, GSC] = {
    "EnableHelp": GsBoolConfig(
        "开启帮助指令",
        "关闭后将不响应 帮助/菜单 指令",
        True,
    ),
    "EnableVersion": GsBoolConfig(
        "开启版本指令",
        "关闭后将不响应 版本 指令",
        True,
    ),
    "EnableMiaoSetting": GsBoolConfig(
        "开启喵喵设置",
        "开启后可用 #喵喵设置 查看与修改本插件配置",
        True,
    ),
    "HelpTitle": GsStrConfig(
        "帮助标题",
        "帮助页主标题",
        "喵喵帮助（GsCore）",
    ),
    "HelpSubTitle": GsStrConfig(
        "帮助副标题",
        "帮助页副标题",
        "Yunzai miao-plugin 的 GsCore 迁移版",
    ),
    "AllowedPanelServers": GsListStrConfig(
        "可选面板服务",
        "展示给用户可选择的面板服务列表",
        ["auto", "miao", "enka", "mgg", "hutao"],
        options=["auto", "miao", "enka", "mgg", "hutao", "mys"],
    ),
    "DefaultPanelServer": GsStrConfig(
        "默认面板服务",
        "用户未设置时使用的默认服务",
        "auto",
        options=["auto", "miao", "enka", "mgg", "hutao", "mys"],
    ),
    "AllowGuestUse": GsBoolConfig(
        "允许游客使用",
        "关闭后，仅管理员可调用本插件命令",
        True,
    ),
    "RecentHistoryLimit": GsIntConfig(
        "历史记录保留条数",
        "每个用户最多保留多少条最近操作记录",
        20,
        max_value=200,
    ),
    "UpdateLogLimit": GsIntConfig(
        "更新日志展示条数",
        "每次显示最近多少条更新记录",
        5,
        max_value=30,
    ),
    "EnableSettingExport": GsBoolConfig(
        "开启设置导出",
        "允许用户通过命令导出当前设置JSON",
        True,
    ),
    "EnableSettingReset": GsBoolConfig(
        "开启设置重置",
        "允许用户通过命令重置个人设置",
        True,
    ),
    "MaxCommaGroup": GsIntConfig(
        "数字分组最大值",
        "#喵喵设置逗号 的最大允许值",
        8,
        max_value=12,
    ),
}
