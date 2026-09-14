"""Split the regulations into one record per article."""
import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
import json
import re
from datetime import date
from pathlib import Path

from ordinals import HEAD, LABEL, REFS, number_of

SRC = Path("data/interim/regulations_clean.txt")
OUT = Path("data/corpus.jsonl")
DOC = "اللائحة التنفيذية لنظام حماية البيانات الشخصية"
URL = "https://sdaia.gov.sa"

flat = re.sub(r"\s+", " ", SRC.read_text(encoding="utf-8"))
flat = re.sub(r"<<<PAGE \d+>>>", " ", flat)

# 1) اجمع بدايات المواد الحقيقية
starts = []
for m in HEAD.finditer(flat):
    n = number_of(m.group(1))
    if n is None:
        continue
    if any(k in flat[m.end():m.end() + 22] for k in REFS):
        continue
    starts.append((n, m.start(), m.end()))

# 2) أول ظهور لكل رقم هو العنوان
first, seen = [], set()
for n, s, e in starts:
    if n not in seen:
        seen.add(n)
        first.append((n, s, e))
first.sort(key=lambda x: x[1])

# 3) نص كل مادة يمتد حتى بداية التالية
records = []
for i, (n, s, e) in enumerate(first):
    end = first[i + 1][1] if i + 1 < len(first) else len(flat)
    body = flat[e:end].strip(" :-–")
    title = re.split(r"[:–-]", body[:80])[0].strip()[:60]
    records.append({
        "id": f"pdpl-reg-art-{n:03d}",
        "doc": DOC,
        "article_no": n,
        "article_label": f"المادة {LABEL[n]}",
        "title": " ".join(title.split()),
        "text": " ".join(body.split()),
        "source_url": URL,
        "retrieved_at": str(date.today()),
    })

records.sort(key=lambda r: r["article_no"])
with OUT.open("w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

lens = [len(r["text"]) for r in records]
print("عدد المواد :", len(records))
print("الأرقام    :", [r["article_no"] for r in records])
print("أقصر مادة  :", min(lens), "حرف")
print("أطول مادة  :", max(lens), "حرف")
print("المتوسط    :", sum(lens) // len(lens), "حرف")
print()
print("--- عينة: المادة الأولى ---")
print(json.dumps(records[0], ensure_ascii=False, indent=2)[:600])
