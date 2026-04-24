from pathlib import Path

from gsuid_core.data_store import get_res_path

from .const import DATA_DIR_NAME

MAIN_PATH = get_res_path() / DATA_DIR_NAME
CONFIG_PATH = MAIN_PATH / "config.json"
HELP_JSON_PATH = MAIN_PATH / "help.json"

MAIN_PATH.mkdir(parents=True, exist_ok=True)
