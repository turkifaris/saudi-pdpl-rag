"""Does including the (sometimes truncated) title help or hurt?"""
import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from metrics import score
from retrieve import load

DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
model = SentenceTransformer("BAAI/bge-m3", device=DEVICE)
recs = load()


class R:
    def __init__(self, vecs):
        self.vecs = vecs

    def search(self, q, k=5):
        qv = model.encode([q], normalize_embeddings=True)[0]
        s = self.vecs @ qv
        return [(float(s[i]), recs[i]) for i in np.argsort(-s)[:k]]


VARIANTS = {
    "title + text": [f"{r['title']} — {r['text']}" for r in recs],
    "text only":    [r["text"] for r in recs],
}

print(f"{'الصيغة':<16}{'Hit@1':>8}{'Hit@5':>8}{'paraph':>8}{'nDCG':>8}")
print("-" * 48)
for label, texts in VARIANTS.items():
    v = model.encode(texts, normalize_embeddings=True, batch_size=4)
    m = score(R(v))
    print(f"{label:<16}{m['overall']['hit1']:>8.2f}{m['overall']['hit5']:>8.2f}"
          f"{m['by_type']['paraphrase']['hit5']:>8.2f}{m['overall']['ndcg']:>8.2f}")
