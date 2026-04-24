from gsuid_core.utils.plugins_config.gs_config import StringConfig

from .config_default import CONFIG_DEFAULT
from .const import PLUGIN_NAME
from .path import CONFIG_PATH

MiaoConfig = StringConfig(
    PLUGIN_NAME,
    CONFIG_PATH,
    CONFIG_DEFAULT,
)
