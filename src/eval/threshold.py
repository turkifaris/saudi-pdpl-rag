"""Rejection threshold measured against answer correctness, not scope alone."""
import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
import json
from pathlib import Path

from rerank import RerankRetriever
from retrieve import load

CACHE = Path("eval/top1_scores.json")
rows = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else None

if rows is None or "correct" not in rows[0]:
    print("حساب الدرجات مع صحة النتيجة الأولى — ~٤ دقائق…")
    r = RerankRetriever(load())
    qs = json.loads(Path("eval/eval_set.json").read_text(encoding="utf-8"))
    rows = []
    for i, q in enumerate(qs, 1):
        score, rec = r.search(q["question"], k=1)[0]
        gold = set(q["gold_articles"])
        rows.append({"id": q["id"], "type": q["type"], "in_scope": bool(gold),
                     "score": score, "correct": rec["article_no"] in gold})
        if i % 20 == 0:
            print(f"  {i}/{len(qs)}")
    CACHE.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")

good = [r for r in rows if r["in_scope"] and r["correct"]]      # يجب ألا تُرفض
wrong = [r for r in rows if r["in_scope"] and not r["correct"]] # رفضها مكسب
outs = [r for r in rows if not r["in_scope"]]                   # يجب أن تُرفض

print(f"\nإجابات صحيحة   : {len(good)}  ← رفضها خسارة")
print(f"إجابات خاطئة   : {len(wrong)}  ← رفضها مكسب")
print(f"خارج النطاق    : {len(outs)}  ← رفضها مطلوب")

print(f"\n{'العتبة':>8}{'خارج النطاق':>14}{'خاطئة مُنعت':>14}{'صحيحة ضاعت':>14}{'':>4}")
print("-" * 54)
best = None
for t in [0.01, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.50]:
    o = sum(1 for r in outs if r["score"] < t)
    w = sum(1 for r in wrong if r["score"] < t)
    g = sum(1 for r in good if r["score"] < t)
    gr = g / len(good)
    mark = ""
    if gr <= 0.05 and (best is None or (o + w) > best[1]):
        best = (t, o + w, o, w, g, gr)
        mark = "◀"
    print(f"{t:>8.2f}{o:>7}/{len(outs)} ({o/len(outs):>3.0%}){w:>7}/{len(wrong)}"
          f"{g:>9}/{len(good)} ({gr:>3.0%}){mark:>4}")
print("-" * 54)

if best:
    t, tot, o, w, g, gr = best
    print(f"\n✅ العتبة: {t:.2f}")
    print(f"   تمنع {o}/{len(outs)} خارج النطاق + {w}/{len(wrong)} إجابة خاطئة = {tot} إجابة سيئة")
    print(f"   وتخسر {g}/{len(good)} إجابة صحيحة ({gr:.0%})")
else:
    print("\n❌ لا عتبة تحقق سقف ٥٪ — التوزيعان متداخلان فعلاً")
