"""Dense retriever over cached corpus embeddings."""
import numpy as np

from embed import MODEL, get_model, query


class DenseRetriever:
    name = "dense"

    def __init__(self, records, emb_path="data/emb_bge-m3.npy",
                 model_name=MODEL, use_prefix=True):
        self.records = records
        self.vecs = np.load(emb_path)
        self.model = get_model(model_name)
        self.use_prefix = use_prefix

    def search(self, q: str, k: int = 5):
        text = query(q) if self.use_prefix else q
        qv = self.model.encode([text], normalize_embeddings=True)[0]
        scores = self.vecs @ qv          # المتجهات موحّدة الطول ⇒ الضرب النقطي = جيب التمام
        order = np.argsort(-scores)[:k]
        return [(float(scores[i]), self.records[i]) for i in order]
