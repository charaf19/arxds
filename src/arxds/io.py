# file: src/arxds/io.py
from __future__ import annotations

import datetime as dt
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any


def save_jsonl(rows: Iterable[dict[str, Any]], path: Path) -> None:
    """Convert datetimes to ISO strings first (why: json can't serialize datetime)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            safe = {k: (v.isoformat() if isinstance(v, dt.datetime) else v) for k, v in r.items()}
            f.write(json.dumps(safe, ensure_ascii=False) + "\n")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows
