"""GsCore loader entry for MiHoYoUID."""

import sys
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parent
if str(PLUGIN_DIR) not in sys.path:
    sys.path.append(str(PLUGIN_DIR))

from MiHoYoUID import *  # noqa: F401,F403,E402
