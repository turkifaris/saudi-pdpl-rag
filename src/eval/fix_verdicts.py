import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
E = ROOT / "eval"

def load(name):
    p = E / name
    if not p.exists():
        sys.exit(f"ناقص: {p}")
    return json.loads(p.read_text(encoding="utf-8"))

CITE    = re.compile(r"[اوفبكل]{0,3}مادة")
REFUSAL = "لا تتضمن المواد المعطاة"

faith    = load("faithfulness.json")
contexts = load("contexts.json")
evalset  = load("eval_set.json")

def index(o, key="id"):
    if isinstance(o, dict):
        return o
    return {r[key]: r for r in o}

QS  = index(evalset["questions"] if isinstance(evalset, dict) and "questions" in evalset else evalset)
CTX = index(contexts)

files = sorted(E.glob("answers_*arabic*.json")) or sorted(E.glob("answers_*.json"))
ANS = index(json.loads(files[0].read_text(encoding="utf-8")))
print("الإجابات من:", files[0].name, "\n")

def text_of(r):
    if isinstance(r, str):
        return r
    for k in ("answer", "text", "output", "response"):
        if k in r:
            return r[k]
    return ""

def shown(qid):
    rec = CTX.get(qid)
    if rec is None:
        return []
    items = rec.get("contexts", rec) if isinstance(rec, dict) else rec
    out = []
    for it in items:
        r = it[1] if isinstance(it, (list, tuple)) else it
        if isinstance(r, dict) and "article_no" in r:
            out.append(int(r["article_no"]))
    return out

pairs = list(faith.items()) if isinstance(faith, dict) else [(r["id"], r) for r in faith]
rows, changed = [], 0

for qid, rec in pairs:
    v = str(rec["verdict"] if isinstance(rec, dict) else rec)
    if v != "5":
        continue
    q       = QS.get(qid, {})
    typ     = q.get("type", "?")
    gold    = [int(g) for g in q.get("gold", [])]
    a       = text_of(ANS.get(qid, ""))
    cited   = bool(CITE.search(a))
    refused = REFUSAL in a
    sh      = shown(qid)

    if typ == "out_of_scope":
        new, why = "1", "خارج النطاق - الرفض صحيح"
    elif cited and not refused:
        new, why = "1", "استشهد بسابقة - خطأ كاشف"
    elif refused and set(gold) & set(sh):
        new, why = "5", "رفض والذهبية معروضة - رفض كاذب حقيقي"
    elif refused:
        new, why = "1", "رفض والذهبية %s لم تعرض - خلل استرجاع" % gold
    else:
        new, why = "1", "لا رفض ولا خطأ"

    rows.append((qid, typ, str(gold), str(sh[:3]), "نعم" if cited else "لا", v, new, why))
    if new != v:
        if isinstance(rec, dict):
            rec["verdict"] = new
            rec["note"] = why
        else:
            faith[qid] = new
        changed += 1

fmt = "{:<7}{:<14}{:<9}{:<13}{:<8}{:>3} -> {:<3} {}"
print(fmt.format("id", "النوع", "ذهبية", "معروض", "استشهد", "من", "الى", "السبب"))
print("-" * 105)
for r in rows:
    print(fmt.format(*r))
print("\nكانت 5:", len(rows), "| صححت:", changed,
      "| رفض كاذب حقيقي:", sum(1 for r in rows if r[6] == "5"))

(E / "faithfulness.json").write_text(json.dumps(faith, ensure_ascii=False, indent=1), encoding="utf-8")
print("حفظ eval/faithfulness.json\n")

for f in ["src/llm_shootout.py", "src/review_faith.py"]:
    p = ROOT / f
    s = p.read_text(encoding="utf-8")
    n, k = re.subn(r'"المادة\\s', r'"[اوفبكل]{0,3}مادة\\s', s)
    if k:
        p.write_text(n, encoding="utf-8")
        print(f, ":", k, "تعديل")
    else:
        print(f, ": لم يعثر على النمط - ارسل لي السطر")
