"""فهرس مؤقت في الذاكرة لمستند مرفوع — يعيد استخدام النماذج المحمَّلة."""
import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
import numpy as np

from embed import get_model
from ordinals import HEAD, number_of


class DocIndex:
    name = "uploaded"

    def __init__(self, records, ce=None, pool: int = 20, batch: int = 8):
        self.records = records
        self.model = get_model()
        self.vecs = self.model.encode([r["text"] for r in records],
                                      normalize_embeddings=True,
                                      batch_size=batch,
                                      show_progress_bar=False)
        self.pool = pool
        if ce is None:
            from rerank import MODEL as CE_MODEL, DEVICE
            from sentence_transformers import CrossEncoder
            ce = CrossEncoder(CE_MODEL, device=DEVICE, max_length=1024)
        self.ce = ce

    def search(self, q: str, k: int = 5):
        qv = self.model.encode([q], normalize_embeddings=True)[0]
        order = np.argsort(-(self.vecs @ qv))[:self.pool]
        cands = [self.records[i] for i in order]
        scores = self.ce.predict([(q, r["text"]) for r in cands], batch_size=8)
        ranked = sorted(zip(scores, cands), key=lambda x: -x[0])
        return [(float(s), r) for s, r in ranked[:k]]


def label_articles(records):
    """يُلحق بكل مقطع أرقام المواد التي يغطّيها — للتقييم فقط."""
    current = None
    for r in records:
        found = []
        for m in HEAD.finditer(r["text"]):
            n = number_of(m.group(1))
            if n:
                found.append(n)
        r["articles"] = sorted(set(([current] if current else []) + found))
        if found:
            current = found[-1]
    return records
