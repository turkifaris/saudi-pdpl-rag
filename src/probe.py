import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from generate import load, RerankRetriever
from dense import DenseRetriever

QS = [
    "ما الفرق بين حقي في الوصول وحقي في التصحيح وحقي في الإتلاف؟",
    "ابي امسح كل شي عني عندهم، يحق لي ولا؟",
    "الشركة خذت رقمي بدون ما اقول اوكي، وش الوضع؟",
    "هم يبيعون معلوماتي لناس ثانية، هذا نظامي؟",
    "ما حقوق صاحب البيانات الشخصية؟",
]

recs = load()
d, r = DenseRetriever(recs), RerankRetriever(recs)

for q in QS:
    print("\n" + "=" * 70)
    print("السؤال:", q)
    print("-" * 70)
    print("dense :", "  ".join(f"م{rec['article_no']}={s:.3f}" for s, rec in d.search(q, k=3)))
    print("rerank:", "  ".join(f"م{rec['article_no']}={s:.3f}" for s, rec in r.search(q, k=3)))
