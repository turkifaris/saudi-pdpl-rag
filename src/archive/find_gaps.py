"""Map found article headings to numbers and locate the gaps."""
import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
import re
from pathlib import Path

UNITS = ["", "الحادية", "الثانية", "الثالثة", "الرابعة", "الخامسة",
         "السادسة", "السابعة", "الثامنة", "التاسعة"]
TENS = {20: "العشرون", 30: "الثلاثون", 40: "الأربعون",
        50: "الخمسون", 60: "الستون"}

ORD = {"الأولى": 1, "الثانية": 2, "الثالثة": 3, "الرابعة": 4, "الخامسة": 5,
       "السادسة": 6, "السابعة": 7, "الثامنة": 8, "التاسعة": 9, "العاشرة": 10}
for i in range(1, 10):
    ORD[f"{UNITS[i]} عشرة"] = 10 + i
for t, word in TENS.items():
    ORD[word] = t
    base = word.replace("ون", "ين")
    for i in range(1, 10):
        ORD[f"{UNITS[i]} و{word}"] = t + i
        ORD[f"{UNITS[i]} و{base}"] = t + i

t = Path("data/interim/regulations_clean.txt").read_text(encoding="utf-8")

found = {}
for m in re.finditer(r"المادة\s+([^\n:]{1,40}):", t):
    label = " ".join(m.group(1).split())
    if label in ORD:
        found[ORD[label]] = label

nums = sorted(found)
print("المواد الموجودة :", nums)
print("العدد           :", len(nums))
print()

if nums:
    missing = [n for n in range(1, max(nums) + 1) if n not in found]
    print("المواد الناقصة  :", missing)
    print()
    rev = {v: k for k, v in ORD.items()}
    for n in missing:
        word = rev[n]
        hits = [ln.strip() for ln in t.split("\n") if word in ln]
        print(f"--- المادة {n} ({word}) — {len(hits)} سطر ---")
        for h in hits[:3]:
            print("   ", h[:110])
        print()
