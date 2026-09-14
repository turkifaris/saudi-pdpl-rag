"""Compare generation models on identical retrieved contexts."""
import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
import json
import re
import time
from pathlib import Path

import requests

from generate import SYSTEM, OLLAMA
from ordinals import ORD

MODELS = [
    "qwen2.5:7b-instruct",
    "command-r7b-arabic",
    "hf.co/Omartificial-Intelligence-Space/ALLaM-7B-Instruct-preview-Q4_K_M-GGUF",
]

REFUSAL_MARK = "لا تتضمن المواد المعطاة"
ARABIC = re.compile(r"[\u0600-\u06FF]")
LATIN_CJK = re.compile(r"[A-Za-z\u4e00-\u9fff]")
ORD_ALT = "|".join(re.escape(k) for k in sorted(ORD, key=len, reverse=True))
CITE_NUM = re.compile(r"[اوفبكل]{0,3}مادة\s*\(?\s*(\d+)")
CITE_ORD = re.compile(r"[اوفبكل]{0,3}مادة\s+(" + ORD_ALT + ")")

rows = json.loads(Path("eval/contexts.json").read_text(encoding="utf-8"))


def cited(text: str) -> set[int]:
    nums = {int(m) for m in CITE_NUM.findall(text)}
    nums |= {ORD[m] for m in CITE_ORD.findall(text)}
    return nums


def run(model: str, row: dict) -> str:
    payload = {"model": model, "stream": False,
               "options": {"temperature": 0.1},
               "messages": [
                   {"role": "system", "content": SYSTEM},
                   {"role": "user", "content":
                    f"المواد المتاحة:\n\n{row['context']}\n\n---\nالسؤال: {row['question']}"}]}
    r = requests.post(OLLAMA, json=payload, timeout=300)
    r.raise_for_status()
    return r.json()["message"]["content"].strip()


results = {}
for model in MODELS:
    short = model.split("/")[-1][:22]
    print(f"\n▶ {short}")
    t0 = time.time()
    n_cite = n_right = n_refuse_ok = n_pure = 0
    lens, answered, out_total = [], 0, 0
    saved = []

    for i, row in enumerate(rows, 1):
        if row["action"] == "refuse":
            continue
        text = run(model, row)
        saved.append({"id": row["id"], "answer": text})
        lens.append(len(text))

        ar = len(ARABIC.findall(text))
        foreign = len(LATIN_CJK.findall(text))
        if ar and foreign / (ar + foreign) < 0.05:
            n_pure += 1

        if not row["gold"]:
            out_total += 1
            if REFUSAL_MARK in text:
                n_refuse_ok += 1
            continue

        answered += 1
        c = cited(text)
        if c:
            n_cite += 1
            if c & set(row["gold"]):
                n_right += 1
        if i % 10 == 0:
            print(f"  {i}/{len(rows)}")

    total = answered + out_total
    results[model] = {
        "cite_rate": n_cite / answered if answered else 0,
        "cite_correct": n_right / answered if answered else 0,
        "refusal": n_refuse_ok / out_total if out_total else 0,
        "purity": n_pure / total if total else 0,
        "avg_len": sum(lens) // len(lens) if lens else 0,
        "secs": time.time() - t0,
    }
    Path(f"eval/answers_{short}.json").write_text(
        json.dumps(saved, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  استشهاد صحيح {results[model]['cite_correct']:.0%} · "
          f"نقاء عربي {results[model]['purity']:.0%} · {results[model]['secs']:.0f}s")

print("\n" + "=" * 76)
print(f"{'النموذج':<26}{'استشهد':>9}{'صحيح':>9}{'رفض':>8}{'عربي':>8}{'طول':>7}{'ثانية':>8}")
print("-" * 76)
for m in MODELS:
    r = results[m]
    print(f"{m.split('/')[-1][:25]:<26}{r['cite_rate']:>8.0%}{r['cite_correct']:>9.0%}"
          f"{r['refusal']:>8.0%}{r['purity']:>8.0%}{r['avg_len']:>7}{r['secs']:>8.0f}")
print("=" * 76)
