"""Evaluate a retriever against the hand-labelled eval set."""
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, median

from retrieve import BM25Retriever, load

K = 10


def dcg(rels):
    return sum(r / math.log2(i + 2) for i, r in enumerate(rels))


def ndcg(rels, n_gold):
    ideal = [1.0] * min(n_gold, len(rels)) + [0.0] * max(0, len(rels) - n_gold)
    d = dcg(ideal)
    return dcg(rels) / d if d else 0.0


recs = load()
retriever = BM25Retriever(recs)
qs = json.loads(Path("eval/eval_set.json").read_text(encoding="utf-8"))

by_type = defaultdict(list)
in_scores, out_scores = [], []

for q in qs:
    hits = retriever.search(q["question"], k=K)
    got = [rec["article_no"] for _, rec in hits]
    top = hits[0][0] if hits else 0.0
    gold = set(q["gold_articles"])

    if not gold:                       # خارج النطاق
        out_scores.append(top)
        continue
    in_scores.append(top)

    rels = [1.0 if a in gold else 0.0 for a in got]
    found = [i for i, x in enumerate(rels) if x]
    by_type[q["type"]].append({
        "hit1": 1.0 if rels[0] else 0.0,
        "hit5": 1.0 if any(rels[:5]) else 0.0,
        "rec5": len(gold & set(got[:5])) / len(gold),
        "mrr":  1 / (found[0] + 1) if found else 0.0,
        "ndcg": ndcg(rels, len(gold)),
    })

allq = [m for v in by_type.values() for m in v]


def agg(ms, key):
    return mean(m[key] for m in ms) if ms else 0.0


print("=" * 62)
print(f"{'':<14}{'عدد':>5}{'Hit@1':>8}{'Hit@5':>8}{'Rec@5':>8}{'MRR':>8}{'nDCG':>8}")
print("-" * 62)
for t in ("direct", "procedural", "paraphrase", "multi"):
    ms = by_type.get(t, [])
    if ms:
        print(f"{t:<14}{len(ms):>5}{agg(ms,'hit1'):>8.2f}{agg(ms,'hit5'):>8.2f}"
              f"{agg(ms,'rec5'):>8.2f}{agg(ms,'mrr'):>8.2f}{agg(ms,'ndcg'):>8.2f}")
print("-" * 62)
print(f"{'الإجمالي':<14}{len(allq):>5}{agg(allq,'hit1'):>8.2f}{agg(allq,'hit5'):>8.2f}"
      f"{agg(allq,'rec5'):>8.2f}{agg(allq,'mrr'):>8.2f}{agg(allq,'ndcg'):>8.2f}")
print("=" * 62)

print("\n--- فصل النطاق (لأجل عتبة الرفض في الأسبوع الرابع) ---")
print(f"  داخل النطاق  ({len(in_scores):>2} سؤال): وسيط {median(in_scores):.2f}  متوسط {mean(in_scores):.2f}")
print(f"  خارج النطاق  ({len(out_scores):>2} سؤال): وسيط {median(out_scores):.2f}  متوسط {mean(out_scores):.2f}")
overlap = sum(1 for s in out_scores if s >= median(in_scores))
print(f"  أسئلة خارج النطاق تتجاوز وسيط الداخل: {overlap}/{len(out_scores)}")
