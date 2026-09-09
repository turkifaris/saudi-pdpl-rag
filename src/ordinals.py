"""Arabic ordinal vocabulary and a bidi-tolerant article-heading pattern."""
import re

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

LABEL = {v: k for k, v in ORD.items() if "ين" not in k}
BARE = {re.sub(r"\s", "", k): v for k, v in ORD.items()}
REFS = ("من النظام", "من هذه اللائحة", "من اللائحة")


def flex(word: str) -> str:
    return r"[\s:]*".join(re.escape(c) for c in word)


def phrase(key: str) -> str:
    return r"[\s:]+".join(flex(w) for w in key.split(" "))


ALT = "|".join(phrase(k) for k in sorted(ORD, key=len, reverse=True))
HEAD = re.compile(flex("المادة") + r"[\s:]+(" + ALT + ")")


def number_of(match_text: str):
    return BARE.get(re.sub(r"[\s:]", "", match_text))
