import json, sys, pathlib, time
import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
from generate import load, RerankRetriever
from rewrite import rewrite

ROOT = pathlib.Path(__file__).resolve().parents[2]
E = ROOT / "eval"

ev = json.loads((E / "eval_set.json").read_text(encoding="utf-8"))
qs = ev["questions"] if isinstance(ev, dict) and "questions" in ev else ev
qs = list(qs.values()) if isinstance(qs, dict) else qs

sample = qs[0]
QKEY = next((k for k in ("q", "question", "text", "سؤال") if k in sample), None)
GKEY = next((k for k in ("gold_articles", "gold", "articles") if k in sample), None)
if not QKEY or not GKEY:
    sys.exit("مفاتيح غير معروفة: " + str(list(sample.keys())))
print(f"حقل السؤال: {QKEY} | حقل الذهبية: {GKEY} | العدد: {len(qs)}\n")

# ١) إعادة الصياغة مرة واحدة وتُخزَّن
cache_p = E / "rewrites.json"
cache = json.loads(cache_p.read_text(encoding="utf-8")) if cache_p.exists() else {}
todo = [q for q in qs if q["id"] not in cache]
for i, q in enumerate(todo, 1):
    new, _ = rewrite(q[QKEY])
    cache[q["id"]] = new
    if i % 10 == 0 or i == len(todo):
        print(f"  صياغة {i}/{len(todo)}")
        cache_p.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
cache_p.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")

# ٢) الاسترجاع على المسارين
r = RerankRetriever(load())
rows = []
t0 = time.time()
for i, q in enumerate(qs, 1):
    gold = {int(x) for x in q.get(GKEY, [])}
    out_of_scope = q.get("type") == "out_of_scope"
    rec = {"id": q["id"], "type": q.get("type"), "oos": out_of_scope, "gold": gold}
    for tag, text in (("raw", q[QKEY]), ("rw", cache[q["id"]])):
        hits = r.search(text, k=5)
        arts = [int(x["article_no"]) for _, x in hits]
        rec[tag] = {"score": hits[0][0], "hit1": arts[0] in gold, "hit5": bool(gold & set(arts))}
    rows.append(rec)
    if i % 15 == 0:
        print(f"  استرجاع {i}/{len(qs)}  ({time.time()-t0:.0f}s)")

json.dump(rows, open(E / "rw_eval_raw.json", "w"), default=list, ensure_ascii=False, indent=1)

ins = [x for x in rows if not x["oos"]]
oos = [x for x in rows if x["oos"]]
print(f"\nداخل النطاق: {len(ins)} | خارجه: {len(oos)}")

print("\n" + "=" * 78)
print("{:<10}{:>10}{:>10}".format("المسار", "Hit@1", "Hit@5"))
print("-" * 78)
for tag, name in (("raw", "بلا صياغة"), ("rw", "مع الصياغة")):
    h1 = sum(x[tag]["hit1"] for x in ins) / len(ins)
    h5 = sum(x[tag]["hit5"] for x in ins) / len(ins)
    print("{:<10}{:>10.3f}{:>10.3f}".format(name, h1, h5))

print("\n" + "=" * 78)
print("مسح العتبات — التغطية (داخل) · الدقة عند الإجابة · الحجب (خارج)")
print("-" * 78)
print("{:<8}{:<12}{:>10}{:>10}{:>10}".format("مسار", "عتبة", "تغطية", "دقة", "حجب خارج"))
for tag, name in (("raw", "بلا"), ("rw", "مع")):
    for t in (0.05, 0.08, 0.15, 0.30, 0.50, 0.70, 0.85):
        kept = [x for x in ins if x[tag]["score"] >= t]
        cov = len(kept) / len(ins)
        prec = (sum(x[tag]["hit1"] for x in kept) / len(kept)) if kept else 0.0
        blk = sum(x[tag]["score"] < t for x in oos) / len(oos)
        print("{:<8}{:<12.2f}{:>10.0%}{:>10.0%}{:>10.0%}".format(name, t, cov, prec, blk))
    print("-" * 78)
