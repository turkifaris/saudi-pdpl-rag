import sys, time, pathlib
import streamlit as st

sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))
from generate import answer, load, RerankRetriever

st.set_page_config(page_title="مستشار الأنظمة السعودية", page_icon="⚖️", layout="centered")

st.markdown("""
<style>
  .stApp, .stApp * { direction: rtl; text-align: right; }
  .stApp code, .stApp pre { direction: ltr; text-align: left; }
  div[data-testid="stTextInput"] input { text-align: right; font-size: 1.05rem; }
  .badge { display:inline-block; padding:.25rem .7rem; border-radius:999px;
           font-size:.85rem; font-weight:600; }
  .answer { font-size:1.15rem; line-height:2.1; padding:1rem 1.2rem;
            border-radius:.6rem; background:rgba(128,128,128,.08);
            border-right:4px solid #888; }
  .meta { color:#888; font-size:.85rem; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource(show_spinner="جارٍ تحميل النماذج… (مرة واحدة فقط)")
def boot():
    records = load()
    return RerankRetriever(records), {int(r["article_no"]): r for r in records}

retriever, by_no = boot()

st.title("⚖️ مستشار الأنظمة السعودية")
st.caption("إجابات مستندة إلى اللائحة التنفيذية لنظام حماية البيانات الشخصية — مع ذكر رقم المادة")

EXAMPLES = [
    "كم مدة الإشعار عن تسرب البيانات؟",
    "هل النظام ينطبق على استخدامي الشخصي لبيانات أصدقائي؟",
    "كيف تثبت الشركة إني وافقت على معالجة بياناتي؟",
]

if "q" not in st.session_state:
    st.session_state.q = ""

st.write("**أمثلة:**")
cols = st.columns(len(EXAMPLES))
for c, ex in zip(cols, EXAMPLES):
    if c.button(ex, use_container_width=True):
        st.session_state.q = ex

q = st.text_input("اكتب سؤالك", value=st.session_state.q, placeholder="مثال: ما حقوق صاحب البيانات؟")
go = st.button("اسأل", type="primary")

if go and q.strip():
    t0 = time.time()
    with st.spinner("جارٍ البحث في اللائحة…"):
        res = answer(q.strip(), retriever)
    secs = time.time() - t0

    style = {
        "answer": ("#1a7f37", "ثقة عالية"),
        "warn":   ("#b26a00", "ثقة منخفضة"),
        "refuse": ("#b3261e", "خارج نطاق اللائحة"),
    }[res["action"]]

    st.markdown(
        f'<span class="badge" style="background:{style[0]}22;color:{style[0]}">'
        f'{style[1]} · {res["score"]:.2f}</span>',
        unsafe_allow_html=True)

    if res.get("rewritten"):
        st.info(f'أُعيدت صياغة سؤالك للبحث: **{res["rewritten"]}**')

    st.markdown(f'<div class="answer">{res["text"]}</div>', unsafe_allow_html=True)

    if res.get("notice"):
        st.warning(res["notice"])

    if res["sources"]:
        st.markdown("#### المواد المعروضة على النموذج")
        for label, no in res["sources"]:
            rec = by_no.get(int(no))
            with st.expander(f"{label}  (مادة {no})"):
                st.write(rec["text"] if rec else "—")
                if rec and rec.get("source_url"):
                    st.markdown(f'<span class="meta">المصدر: {rec["source_url"]}</span>',
                                unsafe_allow_html=True)

    st.markdown(f'<span class="meta">زمن الاستجابة: {secs:.1f} ثانية</span>',
                unsafe_allow_html=True)

st.divider()
st.caption("مشروع بحثي — ليس استشارة قانونية. المرجع الرسمي هو نص اللائحة المنشور من سدايا.")
