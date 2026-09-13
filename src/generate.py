"""End-to-end answering: retrieve → rerank → policy → grounded generation."""
import sys
import textwrap

import requests

from policy import decide
from rerank import RerankRetriever
from retrieve import load

OLLAMA = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:7b-instruct"
TOP_K = 3

SYSTEM = """أنت مساعد يجيب على الأسئلة من اللائحة التنفيذية لنظام حماية البيانات الشخصية السعودي.

قواعد إلزامية:
1. أجب **فقط** من المواد المعطاة أدناه. لا تستخدم أي معرفة خارجها.
2. اذكر رقم المادة التي استندت إليها بصيغة (المادة كذا).
3. إذا لم تجد الجواب في المواد المعطاة، قل حرفياً: «لا تتضمن المواد المعطاة إجابة على هذا السؤال.»
4. لا تخمّن، ولا تكمل من عندك، ولا تستشهد بمادة غير معطاة.
5. أجب بالعربية الفصحى، باختصار، في ٣ جمل أو أقل."""


def build_context(hits) -> str:
    parts = []
    for score, rec in hits:
        parts.append(f"[{rec['article_label']}]\n{rec['text']}")
    return "\n\n".join(parts)


def ask_model(question: str, context: str) -> str:
    payload = {
        "model": MODEL,
        "stream": False,
        "options": {"temperature": 0.1},
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user",
             "content": f"المواد المتاحة:\n\n{context}\n\n---\nالسؤال: {question}"},
        ],
    }
    r = requests.post(OLLAMA, json=payload, timeout=180)
    r.raise_for_status()
    return r.json()["message"]["content"].strip()


def answer(question: str, retriever) -> dict:
    hits = retriever.search(question, k=TOP_K)
    top = hits[0][0]
    action, notice = decide(top)

    if action == "refuse":
        return {"action": action, "score": top, "text": notice, "sources": []}

    text = ask_model(question, build_context(hits))
    return {
        "action": action,
        "score": top,
        "text": text,
        "notice": notice,
        "sources": [(r["article_label"], r["article_no"]) for _, r in hits],
    }


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "كم مدة الإشعار عن تسرب البيانات؟"
    res = answer(q, RerankRetriever(load()))

    print(f"\nالسؤال : {q}")
    print(f"الثقة  : {res['score']:.3f}  →  {res['action']}")
    print("=" * 60)
    print(textwrap.fill(res["text"], width=58))
    if res.get("notice"):
        print(f"\n{res['notice']}")
    if res["sources"]:
        print("\nالمواد المعروضة:")
        for label, no in res["sources"]:
            print(f"  · {label} (#{no})")
