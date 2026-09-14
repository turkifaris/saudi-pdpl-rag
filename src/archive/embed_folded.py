import json, sys, pathlib
import numpy as np
import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
from embed import get_model, CORPUS
from arabic import fold

OUT = pathlib.Path("data/emb_folded.npy")
recs = [json.loads(l) for l in CORPUS.read_text(encoding="utf-8").splitlines()]
vecs = get_model().encode([fold(r["text"]) for r in recs],
                          normalize_embeddings=True, batch_size=8)
np.save(OUT, vecs)
print(f"المواد: {len(recs)} | الشكل: {vecs.shape} | محفوظ: {OUT}")
