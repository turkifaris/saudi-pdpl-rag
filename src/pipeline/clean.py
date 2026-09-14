"""Normalize encoding and strip extraction artifacts."""
import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
import re
import unicodedata
from pathlib import Path

SRC = Path("data/interim/regulations_plain.txt")
DST = Path("data/interim/regulations_clean.txt")

NUM_LINE = re.compile(r"^\s*\d+\s*$")
HEADING = re.compile(r"^المادة\s+[^\n:]{1,40}:", re.M)
ANY = re.compile(r"المادة\s+[^\n:]{1,40}:")


def clean(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    kept = []
    for line in text.split("\n"):
        if NUM_LINE.match(line):
            continue
        kept.append(re.sub(r"[ \t]+", " ", line).strip())
    text = "\n".join(kept)
    return re.sub(r"\n{3,}", "\n\n", text)


if __name__ == "__main__":
    t = clean(SRC.read_text(encoding="utf-8"))
    DST.write_text(t, encoding="utf-8")

    print("الأحرف بعد التنظيف :", len(t))
    print("عناوين في بداية سطر:", len(HEADING.findall(t)))
    print("عناوين في أي موضع  :", len(ANY.findall(t)))
    print()
    for h in ANY.findall(t):
        print("  -", " ".join(h.split()))
