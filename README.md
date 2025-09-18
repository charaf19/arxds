# arxds — arXiv Dataset Suite

**CLI to fetch arXiv papers by time windows, filter (language/length), deduplicate, perform temporal splits, and save JSONL datasets.**

## Quickstart
```bash
python -m venv .venv && . .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -e .
arxds --help
arxds build --cat cs.CL --cat cs.LG --cat cs.AI --cat econ.EM --target 4000 --cutoff 2023-01-01T00:00:00Z --outdir ./out
arxds stats ./out/raw.jsonl
````

## Why

* Reproducible dataset creation for ML/NLP evals.
* Windowed fetching avoids API overload; temporal split prevents leakage.

## Install

```bash
pip install arxds
```

*(after first PyPI release)*

## Docs

* [https://your-org.github.io/arxds/](https://your-org.github.io/arxds/)

## License

Apache-2.0. Not affiliated with arXiv.

# file: CHANGELOG.md

# Changelog

## 0.1.0

* Initial release: build/fetch/stats CLI; JSONL outputs; basic tests and docs.

# file: CONTRIBUTING.md

# Contributing

* Create an issue before big changes.
* Run: `pre-commit install`; `pytest`; `ruff check`; `black --check`.
* For live API tests, set `ARXDS_TEST_LIVE=1` (not required for PRs).
