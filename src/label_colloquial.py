import json, sys, pathlib, re
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from generate import load
from dense import DenseRetriever

E = pathlib.Path(__file__).resolve().parents[1] / "eval"
OUT = E / "colloquial.json"

QS = [
    ("داخل", "الموافقه على معالجه البيانات كيف تكون ؟"),
    ("داخل", "هل لازم يوفرون وسائل للتواصل ؟"),
    ("داخل", "متى يفصح عن بياناتي ؟"),
    ("داخل", "كيف يتم تصحيح بياناتي ؟"),
    ("داخل", "متى يقولون لي عن تسرب البيانات ؟"),
    ("داخل", "اذا جمعو معلومات عشان امور بحثيه ما وافقت وش اسوي ؟"),
    ("داخل", "هل تقويم الاثر الزامي"),
    ("داخل", "ماهي الامور الي يحصد فيها الاثر"),
    ("داخل", "وش الي لازم تكون داخل تقويم الاثر"),
    ("داخل", "اذا ابي اسوي تسويق وش الي التزم فيه"),
    ("داخل", "كم فتره الاحتفاظ بسجلات الانشطه"),
    ("داخل", "وش لازم يكون محتى سجل الانشطه"),
    ("داخل", "وش شرط اختيار جهه المهالجه"),
    ("داخل", "وش الاتفاق مع الي بتعالج بياناتي الجهه"),
    ("داخل", "هل استطيع نقل البيانات خارج المملكة"),
    ("داخل", "كم سنه يتم الاحتفاظ ببياناتي"),
    ("خارج", "كم عقوبه الي سرب بيانات متعمد ؟"),
    ("خارج", "وش يسمى التجسس في هذي القواعد حقت البينات؟"),
    ("خارج", "و تقول الماده 40 ؟"),
    ("خارج", "وش اسوي اذا ماقدرت انقل بياناتي"),
    ("خارج", "الحين البيانات تنتهك بسرعه"),
    ("خارج", "كم مجموعه الغرامات ؟"),
]

recs = load()
d = DenseRetriever(recs)
done = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}

print("""
لكل سؤال: اقرأ المرشحات، ثم اكتب أرقام المواد الصحيحة مفصولة بمسافة.
  مثال:  7        أو   5 7 8
  0 = لا توجد مادة (خارج النطاق فعلاً)
  s = تخطَّ        q = احفظ واخرج
""")

for i, (kind, q) in enumerate(QS, 1):
    qid = f"c{i:03d}"
    if qid in done:
        continue
    print("\n" + "=" * 76)
    print(f"[{qid}] [{kind}]  {q}")
    print("-" * 76)
    for s, r in d.search(q, k=8):
        snip = re.sub(r"\s+", " ", r["text"])[:150]
        print(f"  م{int(r['article_no']):>2}  ({s:.3f})  {snip}…")
    print("-" * 76)
    ans = input("المواد الصحيحة ← ").strip()
    if ans == "q":
        break
    if ans == "s":
        continue
    gold = [] if ans in ("0", "") else [int(x) for x in ans.split()]
    done[qid] = {"id": qid, "question": q, "type": "colloquial" if kind == "داخل" else "out_of_scope",
                 "gold_articles": gold}
    OUT.write_text(json.dumps(done, ensure_ascii=False, indent=1), encoding="utf-8")

print(f"\nمحفوظ: {len(done)}/{len(QS)} في {OUT}")
