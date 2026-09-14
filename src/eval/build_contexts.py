"""Retrieve once; the generation shootout reuses the same contexts."""
import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
import json
import random
from pathlib import Path

from policy import decide
from rerank import RerankRetriever
from retrieve import load

OUT = Path("eval/contexts.json")
N_IN, N_OUT = 20, 10

qs = json.loads(Path("eval/eval_set.json").read_text(encoding="utf-8"))
random.seed(11)
ins = random.sample([q for q in qs if q["gold_articles"]], N_IN)
outs = [q for q in qs if not q["gold_articles"]][:N_OUT]

r = RerankRetriever(load())
rows = []
for i, q in enumerate(ins + outs, 1):
    hits = r.search(q["question"], k=3)
    action, _ = decide(hits[0][0])
    rows.append({
        "id": q["id"], "type": q["type"], "question": q["question"],
        "gold": q["gold_articles"], "score": hits[0][0], "action": action,
        "context": "\n\n".join(f"[{rec['article_label']}]\n{rec['text']}"
                               for _, rec in hits),
        "shown": [rec["article_no"] for _, rec in hits],
    })
    if i % 10 == 0:
        print(f"  {i}/{len(ins)+len(outs)}")

OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n{len(rows)} سؤالاً محفوظاً — منها {sum(1 for x in rows if x['action']=='refuse')} سيُرفض قبل التوليد")
