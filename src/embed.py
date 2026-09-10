"""Encode the corpus into dense vectors and cache them to disk."""
import json
from pathlib import Path

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

MODEL = "BAAI/bge-m3"
OUT = Path("data/emb_bge-m3.npy")
CORPUS = Path("data/corpus.jsonl")

DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"


def get_model(name: str = MODEL) -> SentenceTransformer:
    return SentenceTransformer(name, device=DEVICE)


def passage(rec: dict) -> str:
    # e5 يشترط بادئة تميّز المستند عن السؤال
    return rec["text"]  # بلا عنوان: مقتطع من النص نفسه فيكرره ويشوّه المتجه


def query(text: str) -> str:
    return text  # bge-m3 بلا بادئة


if __name__ == "__main__":
    recs = [json.loads(l) for l in CORPUS.read_text(encoding="utf-8").splitlines()]
    model = get_model()

    print(f"النموذج : {MODEL}")
    print(f"الجهاز  : {DEVICE}")
    print(f"المواد  : {len(recs)}")

    vecs = model.encode(
        [passage(r) for r in recs],
        normalize_embeddings=True,
        show_progress_bar=True,
        batch_size=8,
    )
    np.save(OUT, vecs)

    print(f"\nالشكل   : {vecs.shape}")
    print(f"محفوظ في: {OUT}  ({OUT.stat().st_size/1024:.0f} كيلوبايت)")
