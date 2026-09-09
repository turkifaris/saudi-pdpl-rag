"""Identify which Unicode blocks the extracted Arabic actually uses."""
import re
import unicodedata
from collections import Counter
from pathlib import Path

t = Path("data/interim/regulations_plain.txt").read_text(encoding="utf-8")


def block(ch):
    o = ord(ch)
    if 0x0600 <= o <= 0x06FF:
        return "Arabic (عادي)"
    if 0xFB50 <= o <= 0xFDFF:
        return "Presentation-A"
    if 0xFE70 <= o <= 0xFEFF:
        return "Presentation-B"
    if 0x200B <= o <= 0x200F:
        return "Invisible"
    if 0x202A <= o <= 0x202E:
        return "Bidi-control"
    if ch.isascii():
        return "ASCII"
    return "Other"


print("--- توزيع المحارف ---")
for k, v in Counter(block(ch) for ch in t).most_common():
    print(f"  {k:18} {v}")

print("\n--- عينة أكواد من سطر حقيقي ---")
for line in t.split("\n"):
    s = line.strip()
    if len(s) > 25:
        print("  النص :", s[:40])
        print("  الأكواد:", [hex(ord(ch)) for ch in s[:12]])
        break

print("\n--- بعد تطبيق NFKC ---")
n = unicodedata.normalize("NFKC", t)
hits = re.findall("المادة" + r"\s+[^\n:]{1,40}", n)
print("  مطابقات 'المادة':", len(hits))
for h in hits[:15]:
    print("   -", " ".join(h.split()))
