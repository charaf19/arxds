# file: src/arxds/cli.py
from __future__ import annotations

import datetime as dt
from datetime import timezone
from pathlib import Path

import typer
from rich.console import Console

from .fetch import FetchConfig, fetch_category_by_windows, transform_results
from .io import load_jsonl, save_jsonl
from .transform import (
    FilterConfig,
    SplitConfig,
    dedup_by_id,
    filter_rows,
    print_balance,
    strip_internal_dt,
    temporal_split,
)
from .transform import (
    stats as compute_stats,
)
from .utils import parse_datetime

app = typer.Typer(add_completion=False, help="arXiv dataset CLI: fetch, filter, split, stats")
console = Console()

# Defaults
DEFAULT_CATEGORIES = ("cs.CL", "cs.LG", "cs.AI", "econ.EM")
DEFAULT_TARGET_PER_CAT = 4000
DEFAULT_WINDOW_DAYS = 30
DEFAULT_API_DELAY_SEC = 3.0
DEFAULT_PAGE_SIZE = 100
DEFAULT_CUTOFF_DATE = dt.datetime(2023, 1, 1, tzinfo=timezone.utc)
DEFAULT_MIN_ABS_LEN = 300
DEFAULT_BACKSTOP_DATE = dt.datetime(2007, 1, 1, tzinfo=timezone.utc)

# ---- Typer option/argument singletons (avoid B008) ----
CAT_OPT = typer.Option(list(DEFAULT_CATEGORIES), "--cat", help="arXiv categories")
TARGET_OPT = typer.Option(DEFAULT_TARGET_PER_CAT, "--target", min=1)
WINDOW_OPT = typer.Option(DEFAULT_WINDOW_DAYS, "--window-days", min=1)
DELAY_OPT = typer.Option(DEFAULT_API_DELAY_SEC, "--delay-sec", min=0.0)
PAGE_OPT = typer.Option(DEFAULT_PAGE_SIZE, "--page-size", min=1, max=2000)
CUTOFF_OPT = typer.Option(
    DEFAULT_CUTOFF_DATE.isoformat(), "--cutoff", help="ISO8601, e.g. 2023-01-01T00:00:00Z"
)
MINABS_OPT = typer.Option(DEFAULT_MIN_ABS_LEN, "--min-abs-len", min=0)
BACKSTOP_OPT = typer.Option(DEFAULT_BACKSTOP_DATE.isoformat(), "--backstop", help="Oldest date")
OUTDIR_OPT = typer.Option(Path("./out"), "--outdir", help="Output directory")
LANG_OPT = typer.Option("en", "--lang", help="Language code for abstracts")

OUTFILE_OPT = typer.Option(Path("./out/raw_only.jsonl"), "--out")
FILE_ARG = typer.Argument(..., exists=True, readable=True, dir_okay=False)


@app.command()
def build(
    categories: list[str] = CAT_OPT,
    target_per_cat: int = TARGET_OPT,
    window_days: int = WINDOW_OPT,
    api_delay_sec: float = DELAY_OPT,
    page_size: int = PAGE_OPT,
    cutoff_date: str = CUTOFF_OPT,
    min_abs_len: int = MINABS_OPT,
    backstop_date: str = BACKSTOP_OPT,
    outdir: Path = OUTDIR_OPT,
    lang: str = LANG_OPT,
) -> None:
    """Full pipeline: fetch → dedup → filter → temporal split → save → stats."""
    fcfg = FetchConfig(
        tuple(categories),
        target_per_cat,
        window_days,
        api_delay_sec,
        page_size,
        parse_datetime(backstop_date),
    )
    filcfg = FilterConfig(min_abs_len=min_abs_len, lang=lang)
    scfg = SplitConfig(cutoff_date=parse_datetime(cutoff_date))

    all_rows: list[dict[str, object]] = []
    console.rule("[bold]Fetching")
    for cat in fcfg.categories:
        raw = fetch_category_by_windows(cat, fcfg)
        console.print(f"[magenta]Fetched {len(raw)} items for {cat} before filtering/dedup[/]")
        rows = transform_results(cat, raw)
        all_rows.extend(rows)

    console.rule("[bold]Deduplicate / Filter / Split")
    deduped = dedup_by_id(all_rows)
    filtered = filter_rows(deduped, filcfg)
    train_dev, test = temporal_split(filtered, scfg)

    filtered_safe = strip_internal_dt(filtered)
    train_dev_safe = strip_internal_dt(train_dev)
    test_safe = strip_internal_dt(test)

    outdir.mkdir(parents=True, exist_ok=True)
    save_jsonl(filtered_safe, outdir / "raw.jsonl")
    save_jsonl(train_dev_safe, outdir / "train_dev.jsonl")
    save_jsonl(test_safe, outdir / "test.jsonl")

    console.rule("[bold]Stats")
    s = compute_stats(filtered_safe)
    console.print(f"Total papers (filtered): {s['total']}")
    console.print(f"Average abstract length: {s['avg_len']:.2f} chars")
    print_balance(train_dev_safe, test_safe, filtered_safe)
    console.print(f"Saved: {outdir/'raw.jsonl'}, {outdir/'train_dev.jsonl'}, {outdir/'test.jsonl'}")


@app.command()
def fetch(
    categories: list[str] = CAT_OPT,
    target_per_cat: int = TARGET_OPT,
    window_days: int = WINDOW_OPT,
    api_delay_sec: float = DELAY_OPT,
    page_size: int = PAGE_OPT,
    backstop_date: str = BACKSTOP_OPT,
    out: Path = OUTFILE_OPT,
) -> None:
    """Fetch only; dump minimal fields to JSONL."""
    fcfg = FetchConfig(
        tuple(categories),
        target_per_cat,
        window_days,
        api_delay_sec,
        page_size,
        parse_datetime(backstop_date),
    )
    all_rows: list[dict[str, object]] = []
    console.rule("[bold]Fetching")
    for cat in fcfg.categories:
        raw = fetch_category_by_windows(cat, fcfg)
        rows = transform_results(cat, raw)
        all_rows.extend(rows)
    save_jsonl(strip_internal_dt(all_rows), out)
    console.print(f"Saved: {out}")


@app.command(name="stats")
def stats_cmd(file: Path = FILE_ARG) -> None:
    """Print summary stats for a JSONL dataset."""
    rows = load_jsonl(file)
    s = compute_stats(rows)
    console.print(f"Total: {s['total']}")
    console.print(f"Average abstract length: {s['avg_len']:.2f} chars")
    from collections import Counter

    from rich.table import Table

    counts = Counter(r["category"] for r in rows)
    table = Table(title="Category counts")
    table.add_column("Category")
    table.add_column("Count")
    for c, n in counts.items():
        table.add_row(c, str(n))
    console.print(table)


if __name__ == "__main__":
    app()
