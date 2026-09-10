"""Reciprocal Rank Fusion of BM25 and dense retrieval."""
from dense import DenseRetriever
from retrieve import BM25Retriever


class HybridRetriever:
    name = "hybrid"

    def __init__(self, records, k_rrf: int = 60, pool: int = 20,
                 w_bm25: float = 0.3, w_dense: float = 1.0):
        self.records = records
        self.bm25 = BM25Retriever(records)
        self.dense = DenseRetriever(records)
        self.k_rrf = k_rrf
        self.pool = pool
        self.weights = {id(self.bm25): w_bm25, id(self.dense): w_dense}

    def search(self, q: str, k: int = 5):
        fused = {}
        for retriever in (self.bm25, self.dense):
            for rank, (_, rec) in enumerate(retriever.search(q, k=self.pool)):
                n = rec["article_no"]
                w = self.weights[id(retriever)]
                fused[n] = fused.get(n, 0.0) + w / (self.k_rrf + rank + 1)

        by_no = {r["article_no"]: r for r in self.records}
        best = sorted(fused.items(), key=lambda x: -x[1])[:k]
        return [(score, by_no[n]) for n, score in best]
