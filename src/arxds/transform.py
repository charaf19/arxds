# file: src/arxds/transform.py
from __future__ import annotations

import datetime as dt
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from langdetect import LangDetectException, detect
from rich.console import Console
from rich.table import Table

console = Console()


@dataclass
class FilterConfig:
    min_abs_len: int
    lang: str


@dataclass
class SplitConfig:
    cutoff_date: dt.datetime


def dedup_by_id(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for r in rows:
        if r["doc_id"] not in by_id:
            by_id[r["doc_id"]] = r
    return list(by_id.values())


def filter_rows(rows: Iterable[dict[str, Any]], fcfg: FilterConfig) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    for r in rows:
        abs_txt = r.get("abstract", "")
        if len(abs_txt) < fcfg.min_abs_len:
            continue
        try:
            if detect(abs_txt) == fcfg.lang:
                filtered.append(r)
        except LangDetectException:
            continue
    return filtered


def pick_updated(r: dict[str, Any], cutoff_default: dt.datetime) -> dt.datetime:
    return r.get("_updated_dt") or r.get("_published_dt") or cutoff_default


def temporal_split(
    rows: Iterable[dict[str, Any]], scfg: SplitConfig
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    train_dev: list[dict[str, Any]] = []
    test: list[dict[str, Any]] = []
    for r in rows:
        if pick_updated(r, scfg.cutoff_date) < scfg.cutoff_date:
            train_dev.append(r)
        else:
            test.append(r)
    return train_dev, test


def strip_internal_dt(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for r in rows:
        r2 = dict(r)
        r2.pop("_updated_dt", None)
        r2.pop("_published_dt", None)
        out.append(r2)
    return out


def stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    counts = Counter(r["category"] for r in rows)
    avg_len = (sum(len(r["abstract"]) for r in rows) / total) if total else 0.0
    return {"total": total, "counts": counts, "avg_len": avg_len}


def print_balance(
    train_dev: list[dict[str, Any]], test: list[dict[str, Any]], all_rows: list[dict[str, Any]]
) -> None:
    total = len(all_rows)
    counts = Counter(r["category"] for r in all_rows)
    test_ratio = (len(test) / total) if total else 0.0
    max_cat_ratio = (max(counts.values()) / total) if total else 0.0
    in_domain_count = sum(counts.get(c, 0) for c in ["cs.CL", "cs.LG", "cs.AI"])
    ood_count = counts.get("econ.EM", 0)
    balance = {
        "Total papers": total,
        "In-domain count (>=3k)": in_domain_count >= 3000,
        "OOD count (>=2k)": ood_count >= 2000,
        "Test set ratio (>=15%)": test_ratio >= 0.15,
        "Max category ratio (<=40%)": max_cat_ratio <= 0.40,
    }
    table = Table(title="Balance Check")
    table.add_column("Metric")
    table.add_column("Value")
    for k, v in balance.items():
        table.add_row(k, str(v))
    console.print(table)
    console.print("[green]Category counts:[/]")
    for cat, count in counts.items():
        console.print(f"- {cat}: {count}")
    console.print(
        f"[blue]Train/Dev: {len(train_dev)} | Test: {len(test)} | Test ratio: {test_ratio:.2%}[/]"
    )
