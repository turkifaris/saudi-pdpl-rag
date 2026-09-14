"""Dense retriever over cached corpus embeddings."""
import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
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
