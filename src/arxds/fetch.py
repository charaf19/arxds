# file: src/arxds/fetch.py
from __future__ import annotations

import datetime as dt
import time
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

import arxiv

from .utils import base_arxiv_id, clean_text, iso_or_none, to_utc


def build_window_query(cat: str, start: dt.datetime, end: dt.datetime) -> str:
    """Spaces around TO are required; client encodes them."""
    start_s = start.strftime("%Y%m%d%H%M")
    end_s = end.strftime("%Y%m%d%H%M")
    return f"cat:{cat} AND submittedDate:[{start_s} TO {end_s}]"


@dataclass
class FetchConfig:
    categories: tuple[str, ...]
    target_per_cat: int
    window_days: int
    api_delay_sec: float
    page_size: int
    backstop_date: dt.datetime


def fetch_search(query: str, limit: int, page_size: int, delay: float) -> list[arxiv.Result]:
    out: list[arxiv.Result] = []
    client = arxiv.Client(page_size=page_size, delay_seconds=delay, num_retries=3)
    search = arxiv.Search(
        query=query,
        max_results=limit,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )
    try:
        for res in client.results(search):
            out.append(res)
            if len(out) >= limit:
                break
    except arxiv.UnexpectedEmptyPageError:
        pass  # intermittent
    except arxiv.ArxivError:
        pass  # keep partial
    return out


def fetch_category_by_windows(cat: str, cfg: FetchConfig) -> list[arxiv.Result]:
    collected: list[arxiv.Result] = []
    end = dt.datetime.now(dt.timezone.utc)
    empty_windows = 0
    while len(collected) < cfg.target_per_cat and end > cfg.backstop_date:
        start = end - dt.timedelta(days=cfg.window_days)
        q = build_window_query(cat, start, end)
        need = cfg.target_per_cat - len(collected)
        batch = fetch_search(
            q, limit=min(1000, need), page_size=cfg.page_size, delay=cfg.api_delay_sec
        )
        collected.extend(batch)
        end = start
        time.sleep(cfg.api_delay_sec)  # polite to API
        empty_windows = empty_windows + 1 if not batch else 0
        if empty_windows >= 4:  # jump back faster on empties
            end = end - dt.timedelta(days=cfg.window_days * 3)
            empty_windows = 0
    return collected


def transform_results(cat: str, results: Iterable[arxiv.Result]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for res in results:
        updated_utc = to_utc(getattr(res, "updated", None))
        published_utc = to_utc(getattr(res, "published", None))
        rows.append(
            {
                "doc_id": base_arxiv_id(res.entry_id),
                "title": clean_text(res.title),
                "abstract": clean_text(res.summary),
                "category": cat,
                "updated": iso_or_none(updated_utc),
                "published": iso_or_none(published_utc),
                "url": res.entry_id,
                "_updated_dt": updated_utc,  # internal
                "_published_dt": published_utc,  # internal
            }
        )
    return rows
