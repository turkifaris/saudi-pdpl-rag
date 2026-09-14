"""List in-scope questions whose top-1 is wrong, for manual label review."""
import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
import json
from pathlib import Path

from rerank import RerankRetriever
from retrieve import load

recs = load()
by_no = {r["article_no"]: r for r in recs}
r = RerankRetriever(recs)
qs = json.loads(Path("eval/eval_set.json").read_text(encoding="utf-8"))

print("راجع كل حالة: هل وسمك خاطئ، أم النظام؟\n")
n = 0
for q in qs:
    gold = set(q["gold_articles"])
    if not gold:
        continue
    hits = r.search(q["question"], k=3)
    if hits[0][1]["article_no"] in gold:
        continue
    n += 1
    print("=" * 68)
    print(f"[{q['id']}] {q['type']}")
    print(f"  السؤال : {q['question']}")
    for g in sorted(gold):
        print(f"  وسمك   : {g:>2} — {by_no[g]['title'][:52]}")
    print("  النظام :")
    for i, (s, rec) in enumerate(hits, 1):
        print(f"     {i}. [{s:.3f}] {rec['article_no']:>2} — {rec['title'][:48]}")
    print("  ← اقرأ المواد وقرر: وسم ناقص؟ نطاق خاطئ؟ أم النظام أخطأ؟")
    print()

print(f"المجموع: {n} حالة للمراجعة")
