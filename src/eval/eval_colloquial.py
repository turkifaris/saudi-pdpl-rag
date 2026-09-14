import json, sys, pathlib, time
import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
from generate import load, RerankRetriever
from rewrite import rewrite

E = pathlib.Path(__file__).resolve().parents[2] / "eval"
data = json.loads((E / "colloquial.json").read_text(encoding="utf-8"))
qs = list(data.values())

cp = E / "rewrites_colloquial.json"
cache = json.loads(cp.read_text(encoding="utf-8")) if cp.exists() else {}
for q in qs:
    if q["id"] not in cache:
        cache[q["id"]], _ = rewrite(q["question"])
        cp.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
print("الصياغات جاهزة\n")

r = RerankRetriever(load())
rows, t0 = [], time.time()
for i, q in enumerate(qs, 1):
    gold = set(q["gold_articles"])
    rec = {"id": q["id"], "q": q["question"], "oos": q["type"] == "out_of_scope", "gold": gold}
    for tag, text in (("raw", q["question"]), ("rw", cache[q["id"]])):
        hits = r.search(text, k=5)
        rec[tag] = {"score": hits[0][0],
                    "hit1": int(hits[0][1]["article_no"]) in gold,
                    "top": int(hits[0][1]["article_no"])}
    rows.append(rec)
    print(f"  {i}/{len(qs)}  ({time.time()-t0:.0f}s)")

import json as _j
_j.dump([{k: (sorted(v) if isinstance(v, set) else v) for k, v in x.items()} for x in rows],
        open(E / "colloquial_raw.json", "w"), ensure_ascii=False, indent=1)

ins = [x for x in rows if not x["oos"]]
oos = [x for x in rows if x["oos"]]

def report(name, pick, T):
    ans = [(x, pick(x, T)) for x in ins]
    ans = [(x, p) for x, p in ans if p]
    cov  = len(ans) / len(ins)
    prec = (sum(x[p]["hit1"] for x, p in ans) / len(ans)) if ans else 0.0
    blk  = sum(not pick(x, T) for x in oos) / len(oos)
    print("{:<34}{:>9.0%}{:>9.0%}{:>10.0%}{:>12.0%}".format(
          name, cov, prec, blk, cov * prec))

def raw_only(x, T):  return "raw" if x["raw"]["score"] >= T else None
def cascade(x, T):
    if x["raw"]["score"] >= T: return "raw"
    if x["rw"]["score"]  >= T: return "rw"
    return None

print("\n" + "=" * 74)
print(f"مجموعة العامّية — {len(ins)} داخل النطاق · {len(oos)} خارجه")
print("-" * 74)
print("{:<34}{:>9}{:>9}{:>10}{:>12}".format("النظام", "تغطية", "دقة", "حجب", "مُجاب وصحيح"))
print("-" * 74)
report("قبل كل شيء (بلا صياغة، 0.08)", raw_only, 0.08)
report("بلا صياغة، العتبة الجديدة 0.70", raw_only, 0.70)
report("التركيب، 0.70", cascade, 0.70)

print("\n" + "=" * 74)
print("تفصيل الأسئلة داخل النطاق:")
for x in ins:
    a, b = x["raw"]["score"], x["rw"]["score"]
    mark = "✅" if (max(a, b) >= 0.70) else "❌"
    print(f"  {mark} {x['q'][:46]:<48} خام {a:.3f} → صياغة {b:.3f}   (ذهبية {sorted(x['gold'])})")


print("\n" + "=" * 74)
print("أسئلة خارج النطاق — أين تتسرّب؟")
for x in oos:
    a, b = x["raw"]["score"], x["rw"]["score"]
    leak = "تسرّب ⚠️" if max(a, b) >= 0.70 else "محجوب ✅"
    print(f"  {leak}  {x['q'][:42]:<44} خام {a:.3f} → صياغة {b:.3f}")

print("\n" + "=" * 74)
print("مسح العتبة على التركيب:")
print("{:<8}{:>9}{:>9}{:>10}{:>12}".format("عتبة", "تغطية", "دقة", "حجب", "مُجاب وصحيح"))
for T in (0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90):
    report(f"{T:.2f}", cascade, T)
