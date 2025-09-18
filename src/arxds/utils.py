# file: src/arxds/utils.py
from __future__ import annotations

import datetime as dt
import re
from datetime import timezone
from typing import Optional


def base_arxiv_id(entry_id: str) -> str:
    """Strip version suffix (avoid vN duplicates)."""
    raw = entry_id.split("/")[-1]
    return re.sub(r"v\d+$", "", raw)


def clean_text(s: Optional[str]) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def to_utc(x: Optional[dt.datetime]) -> Optional[dt.datetime]:
    if not x:
        return None
    return x.astimezone(timezone.utc) if x.tzinfo else x.replace(tzinfo=timezone.utc)


def iso_or_none(x: Optional[dt.datetime]) -> Optional[str]:
    return x.isoformat() if x else None


def parse_datetime(s: str) -> dt.datetime:
    """Accept ISO8601; allow trailing 'Z' (why: common in CLI)."""
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    d = dt.datetime.fromisoformat(s)
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
