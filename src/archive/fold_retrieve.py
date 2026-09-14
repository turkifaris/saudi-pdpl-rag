"""استرجاع على نسخة موحَّدة إملائياً — يرجّع السجلات الأصلية دائماً."""
import sys, pathlib
import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
from dense import DenseRetriever
from arabic import fold

class FoldedRetriever:
    name = "folded"

    def __init__(self, records, ce=None, pool: int = 20):
        self.by_id = {r["id"]: r for r in records}
        folded     = [{**r, "text": fold(r["text"])} for r in records]
        self.base  = DenseRetriever(folded, emb_path="data/emb_folded.npy")
        self.pool  = pool
        if ce is None:
            from rerank import MODEL as CE_MODEL, DEVICE
            from sentence_transformers import CrossEncoder
            ce = CrossEncoder(CE_MODEL, device=DEVICE, max_length=1024)
        self.ce = ce

    def search(self, q: str, k: int = 5):
        fq     = fold(q)
        cands  = self.base.search(fq, k=self.pool)
        pairs  = [(fq, rec["text"]) for _, rec in cands]
        scores = self.ce.predict(pairs, batch_size=8)
        ranked = sorted(zip(scores, (rec for _, rec in cands)), key=lambda x: -x[0])
        return [(float(s), self.by_id[rec["id"]]) for s, rec in ranked[:k]]
