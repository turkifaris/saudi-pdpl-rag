"""Manual faithfulness review: compare each answer against its cited article."""
import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
import json
import re
import textwrap
from pathlib import Path

from ordinals import ORD
from retrieve import load

MODEL_FILE = "eval/answers_command-r7b-arabic.json"
OUT = Path("eval/faithfulness.json")

ORD_ALT = "|".join(re.escape(k) for k in sorted(ORD, key=len, reverse=True))
CITE_NUM = re.compile(r"[اوفبكل]{0,3}مادة\s*\(?\s*(\d+)")
CITE_ORD = re.compile(r"[اوفبكل]{0,3}مادة\s+(" + ORD_ALT + ")")

recs = {r["article_no"]: r for r in load()}
ctx = {r["id"]: r for r in json.loads(Path("eval/contexts.json").read_text(encoding="utf-8"))}
answers = json.loads(Path(MODEL_FILE).read_text(encoding="utf-8"))
done = {r["id"]: r for r in json.loads(OUT.read_text(encoding="utf-8"))} if OUT.exists() else {}

print("""
لكل إجابة: اقرأها، ثم اقرأ نص المادة، ثم احكم.

  1 = مدعومة بالكامل   كل ادعاء في الإجابة موجود في المادة
  2 = ناقصة            صحيحة لكنها أغفلت جزءاً مهماً من الجواب
  3 = هلوسة            تحتوي ادعاءً غير موجود في المادة
  4 = بلا استشهاد      لم تذكر رقم مادة
  5 = رفض خاطئ         قال «لا تتضمن» رغم أن المادة الصحيحة معروضة عليه
  s = تخطَّ            q = احفظ واخرج
""")

for a in answers:
    if a["id"] in done:
        continue
    row = ctx[a["id"]]
    nums = {int(m) for m in CITE_NUM.findall(a["answer"])}
    nums |= {ORD[m] for m in CITE_ORD.findall(a["answer"])}

    print("=" * 72)
    print(f"[{a['id']}] {row['type']}   ثقة {row['score']:.3f}")
    print(f"السؤال : {row['question']}")
    print("-" * 72)
    print("الإجابة:")
    print(textwrap.fill(a["answer"], width=70, initial_indent="  ", subsequent_indent="  "))
    print("-" * 72)
    if nums:
        for n in sorted(nums):
            if n in recs:
                print(f"نص {recs[n]['article_label']}:")
                print(textwrap.fill(recs[n]["text"][:900], width=70,
                                    initial_indent="  ", subsequent_indent="  "))
            else:
                print(f"⚠️  استشهد بالمادة {n} — غير موجودة في الكوربوس!")
    else:
        print("⚠️  لا استشهاد")
    print(f"\nالمواد الصحيحة: {row['gold'] or 'خارج النطاق'}")

    v = input("\nالحكم [1/2/3/4/5/s/q] ← ").strip().lower()
    if v == "q":
        break
    if v == "s":
        continue
    note = input("ملاحظة (اختياري) ← ").strip() if v in ("2", "3", "5") else ""
    done[a["id"]] = {"id": a["id"], "type": row["type"], "verdict": v, "note": note}
    OUT.write_text(json.dumps(list(done.values()), ensure_ascii=False, indent=1),
                   encoding="utf-8")

rows = list(done.values())
if rows:
    from collections import Counter
    c = Counter(r["verdict"] for r in rows)
    n = len(rows)
    print("\n" + "=" * 50)
    print(f"مُراجَع: {n}")
    for k, label in [("1", "مدعومة بالكامل"), ("2", "ناقصة"),
                     ("3", "هلوسة"), ("4", "بلا استشهاد"),
                     ("5", "رفض خاطئ")]:
        print(f"  {label:<18} {c.get(k,0):>3}  ({c.get(k,0)/n:>4.0%})")
    attempted = n - c.get("5", 0)
    faith = (c.get("1", 0) + c.get("2", 0)) / attempted if attempted else 0
    print(f"\n  Faithfulness (1+2 من {attempted} محاولة إجابة): {faith:.0%}")
    print(f"  معدل الهلوسة  : {c.get('3',0)/attempted:.0%}" if attempted else "")
    print(f"  رفض خاطئ      : {c.get('5',0)}/{n}  ({c.get('5',0)/n:.0%})")
