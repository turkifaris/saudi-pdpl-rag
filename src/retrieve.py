"""BM25 baseline retriever — lexical only, no models."""
import json
import sys
from pathlib import Path

from rank_bm25 import BM25Okapi
from normalize import tokenize

CORPUS = Path("data/corpus.jsonl")


def load():
    return [json.loads(l) for l in CORPUS.read_text(encoding="utf-8").splitlines()]


class BM25Retriever:
    def __init__(self, records):
        self.records = records
        # العنوان + النص: العنوان مركّز فيضيف إشارة قوية
        corpus = [tokenize(f"{r['title']} {r['text']}") for r in records]
        self.bm25 = BM25Okapi(corpus)

    def search(self, query: str, k: int = 5):
        scores = self.bm25.get_scores(tokenize(query))
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return [(float(scores[i]), self.records[i]) for i in ranked[:k]]


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "كم مدة الإشعار عن تسرب البيانات؟"
    r = BM25Retriever(load())

    print("السؤال:", q)
    print("الرموز:", tokenize(q))
    print("=" * 65)
    for rank, (score, rec) in enumerate(r.search(q), 1):
        print(f"{rank}. [{score:5.2f}]  {rec['article_label']} — {rec['title'][:45]}")
        print(f"           {rec['text'][:110]}...")
        print()
