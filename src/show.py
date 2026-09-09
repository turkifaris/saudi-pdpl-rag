"""Print one article by number:  python src/show.py 14"""
import json
import sys
from pathlib import Path

n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
recs = {json.loads(l)["article_no"]: json.loads(l)
        for l in Path("data/corpus.jsonl").read_text(encoding="utf-8").splitlines()}

r = recs.get(n)
if not r:
    print(f"لا توجد مادة برقم {n} (المتاح 1–{max(recs)})")
else:
    print(f"{r['article_label']}  —  {len(r['text'])} حرف")
    print(f"العنوان: {r['title']}")
    print("=" * 60)
    print(r["text"])
