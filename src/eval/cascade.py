import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
import json, pathlib
E = pathlib.Path(__file__).resolve().parents[2] / "eval"
rows = json.loads((E / "rw_eval_raw.json").read_text(encoding="utf-8"))
ins = [x for x in rows if not x["oos"]]
oos = [x for x in rows if x["oos"]]

def run(T):
    ans = []
    for x in ins:
        if x["raw"]["score"] >= T:   ans.append(("raw", x["raw"]["hit1"]))
        elif x["rw"]["score"] >= T:  ans.append(("rw",  x["rw"]["hit1"]))
    blocked = sum(x["raw"]["score"] < T and x["rw"]["score"] < T for x in oos)
    cov  = len(ans) / len(ins)
    prec = (sum(h for _, h in ans) / len(ans)) if ans else 0.0
    used = sum(p == "rw" for p, _ in ans)
    return cov, prec, blocked / len(oos), used

print("{:<8}{:>10}{:>9}{:>11}{:>13}{:>12}".format(
      "عتبة", "تغطية", "دقة", "حجب خارج", "مُجاب وصحيح", "استخدم صياغة"))
print("-" * 66)
for T in (0.15, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.85, 0.90):
    cov, prec, blk, used = run(T)
    print("{:<8.2f}{:>10.0%}{:>9.0%}{:>11.0%}{:>13.0%}{:>12}".format(
          T, cov, prec, blk, cov * prec, used))
