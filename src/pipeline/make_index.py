"""Reference sheet of all articles, for writing eval questions."""
import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
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
