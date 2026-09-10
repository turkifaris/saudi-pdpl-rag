"""Validate the eval set: schema, coverage, and lexical-leak detection."""
import json
from collections import Counter
from pathlib import Path

from normalize import tokenize

TYPES = {"direct", "procedural", "paraphrase", "multi", "out_of_scope"}
TARGET = {"direct": .30, "procedural": .30, "paraphrase": .20, "multi": .10, "out_of_scope": .10}

arts = {json.loads(l)["article_no"]: json.loads(l)
        for l in Path("data/corpus.jsonl").read_text(encoding="utf-8").splitlines()}
qs = json.loads(Path("eval/eval_set.json").read_text(encoding="utf-8"))

errors, leaks = [], []
ids = set()

for q in qs:
    qid = q.get("id", "?")
    if qid in ids:
        errors.append(f"{qid}: معرّف مكرر")
    ids.add(qid)
    if q.get("type") not in TYPES:
        errors.append(f"{qid}: نوع غير معروف '{q.get('type')}'")
    gold = q.get("gold_articles", [])
    if q.get("type") == "out_of_scope":
        if gold:
            errors.append(f"{qid}: خارج النطاق ويجب أن يكون gold فارغاً")
        continue
    if not gold:
        errors.append(f"{qid}: بلا مادة صحيحة")
    for n in gold:
        if n not in arts:
            errors.append(f"{qid}: المادة {n} غير موجودة")
            continue
        if q["type"] not in ("paraphrase", "multi"):
            continue
        qt = set(tokenize(q["question"]))
        at = set(tokenize(arts[n]["title"] + " " + arts[n]["text"]))
        if qt and len(qt & at) / len(qt) >= 0.8:
            leaks.append((qid, round(len(qt & at) / len(qt), 2), q["question"][:45]))

counts = Counter(q.get("type") for q in qs)
n = len(qs)

print(f"عدد الأسئلة: {n}")
print()
print(f"{'النوع':<14}{'العدد':>6}{'النسبة':>9}{'المستهدف':>10}")
for t in ["direct", "procedural", "paraphrase", "multi", "out_of_scope"]:
    c = counts.get(t, 0)
    print(f"{t:<14}{c:>6}{c/n:>8.0%}{TARGET[t]:>10.0%}")

covered = {a for q in qs for a in q.get("gold_articles", [])}
print()
print(f"تغطية المواد: {len(covered)}/38")
missing = [a for a in sorted(arts) if a not in covered]
if missing:
    print("مواد بلا أسئلة:", missing)

if leaks:
    print("\n⚠️  تسرّب لفظي (نسخت ألفاظ المادة) — أعد الصياغة:")
    for qid, r, txt in leaks:
        print(f"   {qid}  تطابق {r:.0%}  {txt}")

if errors:
    print("\n❌ أخطاء:")
    for e in errors:
        print("   ", e)
else:
    print("\n✅ لا أخطاء بنيوية")
