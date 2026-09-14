import sys, pathlib
import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
from generate import load, RerankRetriever
from fold_retrieve import FoldedRetriever

CASES = [
    ("فشل",  "هل تقويم الاثر الزامي", [25]),
    ("فشل",  "ماهي الامور الي يحصد فيها الاثر", [25]),
    ("فشل",  "وش لازم يكون محتى سجل الانشطه", [33]),
    ("نجاح", "الموافقه على معالجه البيانات كيف تكون ؟", [11]),
    ("نجاح", "متى يقولون لي عن تسرب البيانات ؟", [24]),
    ("خارج", "كم عقوبه الي سرب بيانات متعمد ؟", []),
    ("خارج", "كم سنه يتم الاحتفاظ ببياناتي", []),
]

recs = load()
r = RerankRetriever(recs)
f = FoldedRetriever(recs, ce=getattr(r, "ce", None))

print("{:<7}{:<40}{:>10}{:>11}{:>9}".format("النوع", "السؤال", "خام", "موحَّد", "الفرق"))
print("-" * 78)
for kind, q, gold in CASES:
    a = r.search(q, k=1)[0]
    b = f.search(q, k=1)[0]
    ga = "✓" if int(a[1]["article_no"]) in gold else "·"
    gb = "✓" if int(b[1]["article_no"]) in gold else "·"
    print("{:<7}{:<40}{:>9.3f}{}{:>10.3f}{}{:>+9.3f}".format(
          kind, q[:38], a[0], ga, b[0], gb, b[0] - a[0]))
