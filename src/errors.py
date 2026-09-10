"""List questions where no gold article appears in the top-5."""
import json
from collections import Counter
from pathlib import Path

from dense import DenseRetriever
from retrieve import load

recs = load()
r = DenseRetriever(recs)
qs = json.loads(Path("eval/eval_set.json").read_text(encoding="utf-8"))
by_no = {x["article_no"]: x for x in recs}

fails, near, counts = [], [], Counter()

for q in qs:
    gold = set(q["gold_articles"])
    if not gold:
        continue
    hits = r.search(q["question"], k=5)
    got = [rec["article_no"] for _, rec in hits]
    if not (gold & set(got)):
        fails.append((q, hits, got))
        counts[q["type"]] += 1
    elif not (gold & {got[0]}):
        near.append((q, got))

print(f"فشل تام (لا مادة صحيحة في الخمسة): {len(fails)}/75")
print("حسب النوع:", dict(counts))
print("=" * 70)

for q, hits, got in fails:
    print(f"\n[{q['id']}] {q['type']}")
    print(f"  السؤال  : {q['question'][:75]}")
    for n in q["gold_articles"]:
        print(f"  المطلوب : {n} — {by_no[n]['title'][:50]}")
    print("  المسترجع:")
    for i, (s, rec) in enumerate(hits[:3], 1):
        print(f"     {i}. [{s:.3f}] {rec['article_no']:>2} — {rec['title'][:45]}")

print("\n" + "=" * 70)
print(f"وُجدت لكن ليست الأولى: {len(near)} سؤالاً")
