from __future__ import annotations

import json

from .path import CONFIG_PATH, MAIN_PATH


def ensure_image_panel_defaults() -> None:
    """Keep panel image output enabled after restarts.

    Older installs may have persisted PanelRenderMode=text in the WebUI config.
    StringConfig keeps persisted values, so changing CONFIG_DEFAULT alone is not
    enough. Patch the persisted config at import time as a safe migration.
    """
    MAIN_PATH.mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.exists():
        return

    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return

    if not isinstance(data, dict):
        return

    mode_cfg = data.get("PanelRenderMode")
    if isinstance(mode_cfg, dict) and mode_cfg.get("data") != "image":
        mode_cfg["data"] = "image"
        CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")