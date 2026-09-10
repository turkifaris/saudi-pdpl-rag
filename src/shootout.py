"""Benchmark four embedding models on the same eval set."""
import gc
import json
import time
from pathlib import Path

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from metrics import score
from retrieve import load

DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

MODELS = [
    ("e5-small",       "intfloat/multilingual-e5-small", True),
    ("bge-m3",         "BAAI/bge-m3", False),
    ("arabic-triplet", "Omartificial-Intelligence-Space/Arabic-Triplet-Matryoshka-V2", False),
    ("gate-arabert",   "Omartificial-Intelligence-Space/GATE-AraBert-v1", False),
]


class Retriever:
    def __init__(self, records, vecs, model, prefix):
        self.records, self.vecs, self.model, self.prefix = records, vecs, model, prefix

    def search(self, q, k=5):
        text = f"query: {q}" if self.prefix else q
        qv = self.model.encode([text], normalize_embeddings=True)[0]
        s = self.vecs @ qv
        order = np.argsort(-s)[:k]
        return [(float(s[i]), self.records[i]) for i in order]


recs = load()
results = {}

for key, name, prefix in MODELS:
    emb = Path(f"data/emb_{key}.npy")
    print(f"\n▶ {key}  ({name})")
    t0 = time.time()

    model = SentenceTransformer(name, device=DEVICE)
    dim = model.get_sentence_embedding_dimension()

    if emb.exists():
        vecs = np.load(emb)
        print(f"  المتجهات محفوظة مسبقاً {vecs.shape}")
    else:
        texts = [(f"passage: {r['title']} — {r['text']}" if prefix
                  else f"{r['title']} — {r['text']}") for r in recs]
        vecs = model.encode(texts, normalize_embeddings=True, batch_size=4)
        np.save(emb, vecs)
        print(f"  بُنيت المتجهات {vecs.shape}")

    results[key] = score(Retriever(recs, vecs, model, prefix))
    results[key]["dim"] = dim
    results[key]["secs"] = time.time() - t0
    print(f"  Hit@5 = {results[key]['overall']['hit5']:.2f}   ({results[key]['secs']:.0f}s)")

    del model
    gc.collect()
    if DEVICE == "mps":
        torch.mps.empty_cache()

Path("eval/shootout.json").write_text(
    json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")

print("\n" + "=" * 78)
print(f"{'النموذج':<17}{'أبعاد':>6}{'Hit@1':>8}{'Hit@5':>8}{'paraph':>8}"
      f"{'multi':>8}{'nDCG':>8}{'رفض':>8}")
print("-" * 78)
for key, _, _ in MODELS:
    r = results[key]
    o, t = r["overall"], r["by_type"]
    print(f"{key:<17}{r['dim']:>6}{o['hit1']:>8.2f}{o['hit5']:>8.2f}"
          f"{t.get('paraphrase',{}).get('hit5',0):>8.2f}"
          f"{t.get('multi',{}).get('hit5',0):>8.2f}"
          f"{o['ndcg']:>8.2f}{str(r['overlap'])+'/'+str(r['n_out']):>8}")
print("=" * 78)
print("عمود «رفض»: كم سؤالاً خارج النطاق تجاوز وسيط الداخل (الأقل أفضل)")
