"""Diagnose extraction issues before cleaning."""
import re
from pathlib import Path

TATWEEL = chr(0x0640)
DIACRITICS = re.compile("[\u064B-\u0652]")
NUM_LINE = re.compile(r"^\s*\d+\s*$")
ARTICLE = re.compile("المادة" + r"\s+[^\n:]{1,40}")

t = Path("data/interim/regulations_plain.txt").read_text(encoding="utf-8")
lines = t.split("\n")

n_empty = sum(1 for l in lines if not l.strip())
n_numeric = sum(1 for l in lines if NUM_LINE.match(l))
n_tatweel = t.count(TATWEEL)
n_diac = len(DIACRITICS.findall(t))

print("إجمالي الأحرف   :", len(t))
print("عدد الأسطر      :", len(lines))
print("أسطر فارغة      :", n_empty)
print("أسطر أرقام فقط  :", n_numeric)
print("محارف التطويل   :", n_tatweel)
print("علامات التشكيل  :", n_diac)

clean = t.replace(TATWEEL, "")
hits = ARTICLE.findall(clean)

print()
print("مطابقات 'المادة':", len(hits))
print()
for h in hits[:20]:
    print("  -", " ".join(h.split()))
