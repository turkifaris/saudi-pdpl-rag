"""Show the exact characters following each 'المادة' occurrence."""
import re
from pathlib import Path

t = Path("data/interim/regulations_clean.txt").read_text(encoding="utf-8")
flat = re.sub(r"\s+", " ", t)

for word in ("السادسة", "السابعة", "الثامنة"):
    print(f"===== {word} =====")
    for m in re.finditer("المادة " + word, flat):
        seg = flat[m.start():m.start() + 32]
        print("  النص :", seg)
        print("  أكواد:", [hex(ord(c)) for c in seg[13:24]])
        print()
