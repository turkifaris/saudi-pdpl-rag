"""Reference sheet of all articles, for writing eval questions."""
import json
from pathlib import Path

recs = sorted(
    (json.loads(l) for l in Path("data/corpus.jsonl").read_text(encoding="utf-8").splitlines()),
    key=lambda r: r["article_no"],
)

lines = ["# فهرس المواد — مرجع لكتابة أسئلة التقييم\n"]
for r in recs:
    lines.append(f"### {r['article_no']} — {r['title'][:55]}")
    lines.append(f"{r['text'][:180]}...\n")

Path("eval/articles_index.md").write_text("\n".join(lines), encoding="utf-8")
print("تم إنشاء eval/articles_index.md —", len(recs), "مادة")
