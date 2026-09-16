import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
import json, time
from ingest_any import extract, chunk
from doc_index import DocIndex, label_articles

ROOT = _p.Path(__file__).resolve().parents[2]
E = ROOT / "eval"

ev = json.loads((E / "eval_set.json").read_text(encoding="utf-8"))
qs = ev["questions"] if isinstance(ev, dict) and "questions" in ev else ev
qs = list(qs.values()) if isinstance(qs, dict) else qs
QK = next(k for k in ("q", "question", "text") if k in qs[0])
GK = next(k for k in ("gold_articles", "gold", "articles") if k in qs[0])
RW = json.loads((E / "rewrites.json").read_text(encoding="utf-8"))

pages, warn = extract((ROOT / "data/raw/pdpl_regulations.pdf").read_bytes())
recs = label_articles(chunk(pages))
idx = DocIndex(recs)
print(f"مقاطع: {len(recs)} | تحذير: {warn or 'لا شيء'}\n")

rows, t0 = [], time.time()
for i, q in enumerate(qs, 1):
    gold = {int(x) for x in q.get(GK, [])}
    rec = {"id": q["id"], "oos": q.get("type") == "out_of_scope", "gold": gold}
    for tag, text in (("raw", q[QK]), ("rw", RW.get(q["id"], q[QK]))):
        hits = idx.search(text, k=5)
        top = set(hits[0][1]["articles"])
        five = {a for _, r in hits for a in r["articles"]}
        rec[tag] = {"score": hits[0][0], "hit1": bool(gold & top), "hit5": bool(gold & five)}
    rows.append(rec)
    if i % 15 == 0:
        print(f"  {i}/{len(qs)}  ({time.time()-t0:.0f}s)")

json.dump([{**r, "gold": sorted(r["gold"])} for r in rows],
          open(E / "upload_eval_raw.json", "w"), ensure_ascii=False, indent=1)

ins = [r for r in rows if not r["oos"]]
oos = [r for r in rows if r["oos"]]
print(f"\nداخل: {len(ins)} | خارج: {len(oos)}")
print("\n{:<12}{:>9}{:>9}".format("المسار", "Hit@1", "Hit@5"))
for tag, name in (("raw", "بلا صياغة"), ("rw", "مع الصياغة")):
    print("{:<12}{:>9.3f}{:>9.3f}".format(
        name, sum(r[tag]["hit1"] for r in ins)/len(ins),
              sum(r[tag]["hit5"] for r in ins)/len(ins)))

def cascade(r, T):
    if r["raw"]["score"] >= T: return "raw"
    if r["rw"]["score"] >= T:  return "rw"
    return None

print("\n{:<8}{:>9}{:>9}{:>10}{:>13}".format("عتبة","تغطية","دقة","حجب","مُجاب وصحيح"))
for T in (0.30, 0.50, 0.60, 0.70, 0.80, 0.85, 0.90):
    ans = [(r, cascade(r, T)) for r in ins]
    ans = [(r, p) for r, p in ans if p]
    cov = len(ans)/len(ins)
    prec = sum(r[p]["hit1"] for r, p in ans)/len(ans) if ans else 0
    blk = sum(cascade(r, T) is None for r in oos)/len(oos)
    print("{:<8.2f}{:>9.0%}{:>9.0%}{:>10.0%}{:>13.0%}".format(T, cov, prec, blk, cov*prec))
