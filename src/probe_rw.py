import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from generate import load, RerankRetriever
from rewrite import rewrite

HELD_OUT = [
    ("داخل", "الموافقه على معالجه البيانات كيف تكون ؟"),
    ("داخل", "هل لازم يوفرون وسائل للتواصل ؟"),
    ("داخل", "متى يفصح عن بياناتي ؟"),
    ("داخل", "كيف يتم تصحيح بياناتي ؟"),
    ("داخل", "متى يقولون لي عن تسرب البيانات ؟"),
    ("داخل", "اذا جمعو معلومات عشان امور بحثيه ما وافقت وش اسوي ؟"),
    ("خارج", "كم عقوبه الي سرب بيانات متعمد ؟"),
    ("خارج", "وش يسمى التجسس في هذي القواعد حقت البينات؟"),
    ("خارج", "و تقول الماده 40 ؟"),
]

r = RerankRetriever(load())

def top(q):
    hits = r.search(q, k=3)
    return hits[0][0], "  ".join(f"م{rec['article_no']}={s:.3f}" for s, rec in hits)

ok_before = ok_after = 0
for kind, q in HELD_OUT:
    new, changed = rewrite(q)
    s_old, t_old = top(q)
    s_new, t_new = top(new) if changed else (s_old, t_old)

    good = lambda s: (s >= 0.08) if kind == "داخل" else (s < 0.08)
    ok_before += good(s_old)
    ok_after  += good(s_new)

    print("\n" + "=" * 74)
    print(f"[{kind}] {q}")
    print("   الصياغة:", new if changed else "(بلا تغيير)")
    print(f"   قبل {'✅' if good(s_old) else '❌'}:", t_old)
    print(f"   بعد {'✅' if good(s_new) else '❌'}:", t_new)

n = len(HELD_OUT)
print("\n" + "=" * 74)
print(f"سليم قبل إعادة الصياغة: {ok_before}/{n}   |   بعدها: {ok_after}/{n}")
print("العتبة: رفض تحت 0.08")
