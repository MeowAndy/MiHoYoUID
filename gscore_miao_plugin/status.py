from .const import PLUGIN_NAME
from .database import MiaoUserHistory
from .store import get_all_user_cfg


async def get_user_config_num() -> int:
    datas = await get_all_user_cfg()
    return len(datas)


async def get_history_num() -> int:
    try:
        datas = await MiaoUserHistory.get_all_data()
    except Exception:
        return 0
    return len(datas)


try:
    from gsuid_core.status.plugin_status import register_status

    register_status(
        None,
        PLUGIN_NAME,
        {
            "用户配置": get_user_config_num,
            "历史记录": get_history_num,
        },
    )
except Exception:
    pass