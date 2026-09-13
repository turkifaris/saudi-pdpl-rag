"""Cross-encoder reranking over dense candidates."""
import torch
from sentence_transformers import CrossEncoder

from dense import DenseRetriever

MODEL = "BAAI/bge-reranker-v2-m3"
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"


class RerankRetriever:
    name = "rerank"

    def __init__(self, records, pool: int = 20, model_name: str = MODEL):
        self.base = DenseRetriever(records)      # المرحلة الأولى: سريعة
        self.pool = pool                          # كم مرشحاً نمرره للمُعيد
        self.ce = CrossEncoder(model_name, device=DEVICE, max_length=1024)

    def search(self, q: str, k: int = 5):
        cands = self.base.search(q, k=self.pool)
        pairs = [(q, rec["text"]) for _, rec in cands]
        scores = self.ce.predict(pairs, batch_size=8)
        ranked = sorted(zip(scores, (rec for _, rec in cands)), key=lambda x: -x[0])
        return [(float(s), rec) for s, rec in ranked[:k]]
