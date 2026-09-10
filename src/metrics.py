"""Shared retrieval metrics."""
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, median

K = 10
TYPES = ("direct", "procedural", "paraphrase", "multi")


def dcg(rels):
    return sum(r / math.log2(i + 2) for i, r in enumerate(rels))


def ndcg(rels, n_gold):
    ideal = [1.0] * min(n_gold, len(rels)) + [0.0] * max(0, len(rels) - n_gold)
    d = dcg(ideal)
    return dcg(rels) / d if d else 0.0


def load_questions():
    return json.loads(Path("eval/eval_set.json").read_text(encoding="utf-8"))


def score(retriever, qs=None):
    qs = qs or load_questions()
    by_type = defaultdict(list)
    in_s, out_s = [], []

    for q in qs:
        hits = retriever.search(q["question"], k=K)
        got = [r["article_no"] for _, r in hits]
        top = hits[0][0] if hits else 0.0
        gold = set(q["gold_articles"])

        if not gold:
            out_s.append(top)
            continue
        in_s.append(top)

        rels = [1.0 if a in gold else 0.0 for a in got]
        found = [i for i, x in enumerate(rels) if x]
        by_type[q["type"]].append({
            "hit1": 1.0 if rels[0] else 0.0,
            "hit5": 1.0 if any(rels[:5]) else 0.0,
            "rec5": len(gold & set(got[:5])) / len(gold),
            "mrr": 1 / (found[0] + 1) if found else 0.0,
            "ndcg": ndcg(rels, len(gold)),
        })

    allq = [m for v in by_type.values() for m in v]
    agg = lambda ms, k: mean(m[k] for m in ms) if ms else 0.0
    med_in = median(in_s)

    return {
        "by_type": {t: {k: agg(by_type[t], k)
                        for k in ("hit1", "hit5", "rec5", "mrr", "ndcg")}
                    for t in TYPES if by_type.get(t)},
        "overall": {k: agg(allq, k) for k in ("hit1", "hit5", "rec5", "mrr", "ndcg")},
        "med_in": med_in,
        "med_out": median(out_s),
        "overlap": sum(1 for s in out_s if s >= med_in),
        "n_out": len(out_s),
    }
