"""GsCore loader entry for gscore_miao-plugin."""

import sys
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parent
if str(PLUGIN_DIR) not in sys.path:
    sys.path.append(str(PLUGIN_DIR))

from gscore_miao_plugin import *  # noqa: F401,F403,E402
