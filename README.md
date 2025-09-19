**TL;DR:** here’s a drop-in `README.md` you can paste. It invites contributions and includes a “Next features” section with bullet-only descriptions (no code).

### Plan

* Keep concise intro + value prop.
* Quickstart (install, CLI help).
* Contributing guide (fork, venv, pre-commit, tests, PR checklist).
* Governance & scope notes.
* Feature proposals: how to suggest + template.
* Roadmap: bullet-only “Next features” list with short descriptions (no code).
* License, citation, acknowledgements.

````md
# arxds — arXiv Dataset Suite

Reproducible arXiv dataset creation for NLP/ML: windowed fetching, deduplication, filtering, temporal splits, and JSONL outputs — with a simple CLI.

- **Why:** avoid data leakage, keep runs reproducible, and make evaluation sets easy to regenerate.
- **What you get:** a Python package + CLI (`arxds`) that fetches arXiv entries by time windows, cleans text, filters on length/language, splits by date, and writes JSONL files.

---

## Quickstart

```bash
pip install arxds
arxds --help
# End-to-end example (small, polite):
arxds build --cat cs.AI --target 50 --window-days 14 --delay-sec 3 --outdir ./out --cutoff 2023-01-01T00:00:00Z
````

> Need dev setup? See **Contributing** below.

---

## Contributing

We welcome issues, discussions, and pull requests. Please follow these steps for a smooth review.

### Dev setup

```bash
git clone https://github.com/<YOUR_USERNAME>/arxds.git
cd arxds
python -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -e .
pip install -r requirements-dev.txt
pre-commit install
pre-commit run --all-files
pytest -q
```

### PR checklist

* [ ] Describes the problem and the solution clearly.
* [ ] `pre-commit run --all-files` clean (Black, Ruff, Codespell, EOL).
* [ ] `pytest` green; add/adjust tests if behavior changes.
* [ ] Docs updated (README/`docs/`), including CLI options if applicable.
* [ ] Changelog entry added if user-facing (`CHANGELOG.md`).

### Governance & scope

* **Scope:** reproducible dataset building from arXiv metadata. Focus on correctness, reproducibility, and ergonomics.
* **Non-goals (for now):** heavy PDF parsing, large-scale crawling beyond arXiv’s API etiquette, proprietary indexers.
* **Style:** PEP8, Black, Ruff; type hints where helpful; short, focused functions; docstrings over verbose comments.

### How to propose a feature

Open a **Feature request** issue and include:

* **Problem / use case:** what research workflow does this unlock?
* **Proposed behavior:** what the CLI/API should do.
* **Inputs/outputs:** flags, environment variables, file formats.
* **Constraints:** rate limits, privacy, reproducibility considerations.
* **Success criteria:** how we’ll know it’s done.

---

## Next features (ideas & contributions welcome)

> Bullet points only; short descriptions; no code.

* **Resumable fetches:** Cache progress and continue from the last successful window to survive interruptions.
* **Incremental updates:** Fetch only new/changed records since a given timestamp, appending safely to existing datasets.
* **Config file support:** Read defaults from `arxds.toml`/`yaml` to avoid long CLI commands and enable reproducible runs.
* **Parallel windowing with rate control:** Modest concurrency with adaptive backoff to respect API limits while speeding runs.
* **Content hashing dedup:** Beyond arXiv IDs, detect near-duplicates via title/abstract hashing (e.g., normalized text hash).
* **Richer filters:** Include/exclude by title/abstract regex, author list size, or presence of certain keywords.
* **Language detection backends:** Pluggable detectors (e.g., fastText, CLD3) with a confidence threshold and fallback.
* **Export formats:** Parquet and DuckDB/SQLite outputs for faster downstream analytics and SQL-friendly workflows.
* **Manifest & provenance:** Emit a run manifest (seed, time, CLI args, category counts, API notes) for reproducibility and audits.
* **Dataset cards:** Auto-generate a lightweight “data card” summarizing scope, filtering, splits, and caveats.
* **Category balancing helpers:** Optional oversampling/undersampling strategies with audit logs of changes.
* **Leakage guardrails:** Warn if `--cutoff` is near “now” or if categories are highly imbalanced; print actionable hints.
* **HF Hub compatibility:** One-command packaging of JSONL + metadata for upload to Hugging Face Datasets (no code, just structure).
* **CLI UX polish:** Progress bars, richer `--verbose` logs, JSON logging mode, colorized summaries.
* **Dry-run mode:** Validate queries and show expected counts without hitting the network aggressively.
* **CI test cassettes:** Record small arXiv responses once and replay in tests to keep CI offline and reliable.
* **Error transparency:** Structured error summary at the end (timeouts, empty windows, backoffs) with suggested next steps.
* **Pluggable splits:** Add k-fold and rolling splits in addition to single `--cutoff` temporal splits.
* **Relevance sampling:** Optional keyword- or embedding-guided sampling to target subtopics without manual filters.
* **Safety & etiquette:** Built-in min delay, randomized jitter, and header notes aligning with arXiv API best practices.

> Have another idea? Open an issue with “Feature:” in the title and follow the template above.

---

## Troubleshooting

* **Empty results:** widen the window (`--window-days`), expand categories, or check backstop date.
* **Rate limits / timeouts:** increase `--delay-sec`, reduce `--target`, or run during off-peak hours.
* **Imbalanced categories:** review counts in the summary; adjust per-category targets or apply balancing helpers.

---

## Release & versioning

* Semantic-style versions. Tags like `v0.1.0` trigger the publish workflow.
* Changelog entries live in `CHANGELOG.md`.

---

## License

Apache-2.0. Not affiliated with arXiv.

---

## Citation

If this tool helped your research, please cite the repository (see `CITATION.cff`).

```

**a.** Want me to also refresh `CONTRIBUTING.md` to match this README (PR checklist, feature template)?
**b.** Should I convert the “Next features” bullets into labeled GitHub issues automatically?
::contentReference[oaicite:0]{index=0}
```
