"""Print everything between article 16 and article 19."""
import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
import re
from pathlib import Path

t = Path("data/interim/regulations_clean.txt").read_text(encoding="utf-8")
flat = re.sub(r"\s+", " ", t)

a = re.search(r"المادة[\s:]*السادسة[\s:]*عشرة", flat)
b = re.search(r"المادة[\s:]*التاسعة[\s:]*عشرة", flat)

if not a or not b:
    print("لم يُعثر على أحد الحدين:", bool(a), bool(b))
else:
    span = flat[a.start():b.start()]
    print("طول المقطع:", len(span), "حرف")
    print("=" * 60)
    for i in range(0, len(span), 300):
        print(span[i:i + 300])
        print("-" * 40)
