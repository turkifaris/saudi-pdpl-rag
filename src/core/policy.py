"""Answer policy: refuse, warn, or answer, based on reranker confidence."""
import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]

REFUSE_BELOW = 0.70   # أقل من ذلك: النظام لم يجد شيئاً
WARN_BELOW   = 0.85     # بين الاثنتين: إجابة مع تحذير

REFUSAL = "لم أجد في اللائحة التنفيذية مادة تجيب هذا السؤال."
WARNING = "⚠️ ثقة منخفضة — يُرجى مراجعة النص الرسمي للمادة."


def decide(top_score: float) -> tuple[str, str | None]:
    """Return (action, notice). action ∈ {refuse, warn, answer}."""
    if top_score < REFUSE_BELOW:
        return "refuse", REFUSAL
    if top_score < WARN_BELOW:
        return "warn", WARNING
    return "answer", None


if __name__ == "__main__":
    for s in (0.005, 0.04, 0.12, 0.29, 0.55, 0.97):
        action, notice = decide(s)
        print(f"  {s:>6.3f}  →  {action:<7} {notice or ''}")
