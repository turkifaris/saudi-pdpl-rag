import json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from ordinals import ORD

E = pathlib.Path(__file__).resolve().parents[1] / "eval"

ALT  = "|".join(sorted(ORD, key=len, reverse=True))
NUM  = re.compile(r"[اوفبكل]{0,3}مادة\s*\(?\s*(\d+)")
ORDR = re.compile(r"[اوفبكل]{0,3}مادة\s+(" + ALT + ")")

ev = json.loads((E/"eval_set.json").read_text(encoding="utf-8"))
qs = ev["questions"] if isinstance(ev, dict) and "questions" in ev else ev
QS = qs if isinstance(qs, dict) else {q["id"]: q for q in qs}

sample = next(iter(QS.values()))
GKEY = next((k for k in ("gold","gold_articles","articles","gold_ids") if k in sample), None)
if not GKEY:
    sys.exit("لم أجد حقل المواد الذهبية. المفاتيح: " + str(list(sample.keys())))
print("حقل الذهبية:", GKEY, "\n")

def cited(t):
    out = {int(m) for m in NUM.findall(t)}
    out |= {int(ORD[m]) for m in ORDR.findall(t)}
    return out

for f in sorted(E.glob("answers_*.json")):
    data = json.loads(f.read_text(encoding="utf-8"))
    items = data.items() if isinstance(data, dict) else [(r["id"], r) for r in data]
    n = c = ok = 0
    for qid, rec in items:
        q = QS.get(qid)
        if not q or q.get("type") == "out_of_scope":
            continue
        t = rec if isinstance(rec, str) else next((rec[k] for k in ("answer","text","output","response") if k in rec), "")
        g = {int(x) for x in q[GKEY]}
        s = cited(t)
        n += 1
        if s: c += 1
        if s & g: ok += 1
    if n:
        print(f"{f.name:<42} استشهد {c}/{n} ({100*c//n}%)   استشهاد صحيح {ok}/{n} ({100*ok//n}%)")
