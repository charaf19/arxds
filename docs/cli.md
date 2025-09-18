# CLI

```bash
arxds build --cat cs.CL --target 1000 --cutoff 2023-01-01T00:00:00Z --outdir ./out
arxds fetch --cat cs.AI --target 200 --out ./out/raw_only.jsonl
arxds stats ./out/raw.jsonl
```
