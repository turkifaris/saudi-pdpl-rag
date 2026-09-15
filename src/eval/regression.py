import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
import json, sys
from statistics import median
from generate import load
from dense import DenseRetriever

ROOT = _p.Path(__file__).resolve().parents[2]
BASE = ROOT / "eval" / "baseline.json"
TOL  = 0.01

ev = json.loads((ROOT / "eval" / "eval_set.json").read_text(encoding="utf-8"))
qs = ev["questions"] if isinstance(ev, dict) and "questions" in ev else ev
qs = list(qs.values()) if isinstance(qs, dict) else qs
QK = next(k for k in ("q", "question", "text") if k in qs[0])
GK = next(k for k in ("gold_articles", "gold", "articles") if k in qs[0])

def run(r):
    ins = [q for q in qs if q.get("type") != "out_of_scope"]
    oos = [q for q in qs if q.get("type") == "out_of_scope"]
    h1 = h5 = 0
    si, so = [], []
    for q in ins:
        g = {int(x) for x in q[GK]}
        hits = r.search(q[QK], k=5)
        arts = [int(x["article_no"]) for _, x in hits]
        h1 += arts[0] in g
        h5 += bool(g & set(arts))
        si.append(hits[0][0])
    for q in oos:
        so.append(r.search(q[QK], k=1)[0][0])
    return {"n": len(ins), "hit1": round(h1/len(ins), 3), "hit5": round(h5/len(ins), 3),
            "med_in": round(median(si), 3), "med_out": round(median(so), 3)}

recs = load()
systems = {"dense": DenseRetriever(recs)}
if "--full" in sys.argv:
    from rerank import RerankRetriever
    systems["rerank"] = RerankRetriever(recs)

now = {k: run(v) for k, v in systems.items()}

if "--save" in sys.argv:
    old = json.loads(BASE.read_text(encoding="utf-8")) if BASE.exists() else {}
    old.update(now)
    BASE.write_text(json.dumps(old, ensure_ascii=False, indent=1), encoding="utf-8")
    print("خط الأساس محفوظ:\n" + json.dumps(old, ensure_ascii=False, indent=1))
    sys.exit(0)

if not BASE.exists():
    sys.exit("لا يوجد خط أساس. شغّل: python src/eval/regression.py --save --full")

base = json.loads(BASE.read_text(encoding="utf-8"))
bad = []
for sysname, cur in now.items():
    exp = base.get(sysname)
    if exp is None:
        print(f"تخطٍّ: {sysname} غير موجود في خط الأساس"); continue
    for k, v in cur.items():
        e = exp[k]
        ok = (v == e) if k == "n" else abs(v - e) <= TOL
        mark = "✅" if ok else "❌"
        print(f"  {mark} {sysname}.{k:<8} متوقع {e}  فعلي {v}")
        if not ok:
            bad.append(f"{sysname}.{k}")

print()
if bad:
    sys.exit("انحدار! تغيّر: " + ", ".join(bad))
print("لا انحدار — النظام كما قِيس.")
