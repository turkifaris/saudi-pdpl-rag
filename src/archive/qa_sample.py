"""Print random articles for manual review."""
import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
import json
import random
from pathlib import Path

recs = [json.loads(l) for l in Path("data/corpus.jsonl").read_text(encoding="utf-8").splitlines()]
random.seed(7)

for r in random.sample(recs, 20):
    print("=" * 70)
    print(f"[{r['article_no']}] {r['article_label']}  ({len(r['text'])} حرف)")
    print(f"العنوان: {r['title']}")
    print("-" * 70)
    print(r["text"][:400])
    print()
