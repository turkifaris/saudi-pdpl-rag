"""Detect article headings despite bidi punctuation and intra-word spacing."""
import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
import re
from pathlib import Path

UNITS = ["", "الحادية", "الثانية", "الثالثة", "الرابعة", "الخامسة",
         "السادسة", "السابعة", "الثامنة", "التاسعة"]
TENS = {20: "العشرون", 30: "الثلاثون", 40: "الأربعون"}

ORD = {"الأولى": 1, "الثانية": 2, "الثالثة": 3, "الرابعة": 4, "الخامسة": 5,
       "السادسة": 6, "السابعة": 7, "الثامنة": 8, "التاسعة": 9, "العاشرة": 10}
for i in range(1, 10):
    ORD[f"{UNITS[i]} عشرة"] = 10 + i
for tn, w in TENS.items():
    for form in (w, w.replace("ون", "ين")):
        ORD[form] = tn
        for i in range(1, 10):
            ORD[f"{UNITS[i]} و{form}"] = tn + i


def flex(word: str) -> str:
    """يسمح بمسافات ونقطتين بين حروف الكلمة الواحدة."""
    return r"[\s:]*".join(re.escape(c) for c in word)


def phrase(key: str) -> str:
    return r"[\s:]+".join(flex(w) for w in key.split(" "))


ALT = "|".join(phrase(k) for k in sorted(ORD, key=len, reverse=True))
HEAD = re.compile(flex("المادة") + r"[\s:]+(" + ALT + ")")


def norm(s: str) -> str:
    return " ".join(re.sub(r"[\s:]+", "", w) for w in re.split(r"[\s:]{2,}|\s(?=[او])", s)) 


t = Path("data/interim/regulations_clean.txt").read_text(encoding="utf-8")
flat = re.sub(r"\s+", " ", t)

seen = {}
for m in HEAD.finditer(flat):
    raw = re.sub(r"[\s:]", "", m.group(1))
    hit = next((n for k, n in ORD.items() if re.sub(r"\s", "", k) == raw), None)
    if hit is None:
        continue
    tail = flat[m.end():m.end() + 60]
    if any(k in tail[:22] for k in ("من النظام", "من هذه اللائحة", "من اللائحة")):
        continue
    seen.setdefault(hit, tail.strip())

found = sorted(seen)
print("مواد لها عنوان :", found)
print("العدد          :", len(found))
print("الناقص         :", [n for n in range(1, 39) if n not in seen])
