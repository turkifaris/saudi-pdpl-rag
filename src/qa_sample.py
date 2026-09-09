"""Print random articles for manual review."""
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
