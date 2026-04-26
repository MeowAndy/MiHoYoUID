from __future__ import annotations

import ast
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "MiHoYoUID" / "artifact_rules"
URLS = {
    "gs": "https://raw.githubusercontent.com/yoimiya-kokomi/miao-plugin/master/resources/meta-gs/artifact/artis-mark.js",
    "sr": "https://raw.githubusercontent.com/yoimiya-kokomi/miao-plugin/master/resources/meta-sr/artifact/artis-mark.js",
}

ENTRY_RE = re.compile(r"^\s*(?P<name>'[^']+'|[\w\u4e00-\u9fff·•&]+)\s*:\s*\{(?P<body>.*?)\}\s*,?\s*$")
PAIR_RE = re.compile(r"(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?P<value>-?\d+(?:\.\d+)?)")


def parse(text: str) -> dict[str, dict[str, float]]:
    data: dict[str, dict[str, float]] = {}
    for line in text.splitlines():
        line = line.split("//", 1)[0].strip()
        if not line:
            continue
        m = ENTRY_RE.match(line)
        if not m:
            continue
        raw_name = m.group("name")
        name = ast.literal_eval(raw_name) if raw_name.startswith("'") else raw_name
        weights = {km.group("key"): float(km.group("value")) for km in PAIR_RE.finditer(m.group("body"))}
        if weights:
            data[name] = weights
    return data


def write_game(game: str, data: dict[str, dict[str, float]]) -> None:
    target = OUT / game
    target.mkdir(parents=True, exist_ok=True)
    init = target / "__init__.py"
    init.write_text("from __future__ import annotations\n\n", encoding="utf-8")
    for name, weights in data.items():
        safe = re.sub(r"[^\w\u4e00-\u9fff]+", "_", name, flags=re.UNICODE).strip("_") or "rule"
        path = target / f"{safe}.py"
        body = [
            "from __future__ import annotations",
            "",
            "from typing import Any, Dict, Tuple",
            "",
            f"CHARACTER_NAME = {name!r}",
            f"BASE_WEIGHT: Dict[str, float] = {dict(weights)!r}",
            "",
            "",
            "def get_rule(char: Dict[str, Any], context: Dict[str, Any]) -> Tuple[str, Dict[str, float]]:",
            "    \"\"\"Return the miao-plugin artifact score rule for this character.\"\"\"",
            "    return context.get('default_title') or f\"{CHARACTER_NAME}-通用\", dict(BASE_WEIGHT)",
            "",
        ]
        path.write_text("\n".join(body), encoding="utf-8")


def main() -> None:
    total = 0
    for game, url in URLS.items():
        text = urllib.request.urlopen(url, timeout=30).read().decode("utf-8")
        data = parse(text)
        write_game(game, data)
        total += len(data)
        print(f"{game}: {len(data)} rules")
    print(f"total: {total}")


if __name__ == "__main__":
    main()
