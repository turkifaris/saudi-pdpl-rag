import sys, time, pathlib, hashlib
import streamlit as st

_SRC = pathlib.Path(__file__).resolve().parent / "src"
sys.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]

from generate import answer, load, RerankRetriever
from pageview import render as render_page, render_from, available as pdf_available
from ingest_any import extract, chunk
from doc_index import DocIndex

UPLOAD_REFUSE = 0.50
UPLOAD_WARN = 0.70
MAX_MB = 20

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


@st.cache_data(show_spinner=False)
def page_png(page_no: int):
    png, _ = render_page(page_no)
    return png


@st.cache_data(show_spinner=False)
def page_png_up(digest: str, page_no: int, _data: bytes):
    return render_from(_data, page_no)


def reset():
    st.session_state.pop("res", None)


st.title("⚖️ مستشار الأنظمة السعودية")

mode = st.radio("المصدر", ["اللائحة التنفيذية", "ملفك"],
                horizontal=True, on_change=reset, label_visibility="collapsed")

ready = False
up_data = None

if mode == "اللائحة التنفيذية":
    st.caption("إجابات مستندة إلى اللائحة التنفيذية لنظام حماية البيانات الشخصية — مع ذكر رقم المادة")
    active_ret, active_by = retriever, by_no
    refuse_t = warn_t = None
    ready = True
else:
    st.caption(f"ارفع مستنداً عربياً واسأل عنه — حتى {MAX_MB} ميغابايت")
    st.warning(
        "**وضع تجريبي.** النظام هنا يقطّع المستند تقطيعاً عاماً لا يعرف بنيته. "
        f"عتبة الرفض ({UPLOAD_REFUSE}) معايَرة على مستند واحد فقط، "
        "والأرقام المنشورة في التوثيق تصف اللائحة التنفيذية لا ملفك."
    )
    up = st.file_uploader("ملف PDF", type=["pdf"], label_visibility="collapsed")

    if up is not None:
        data = up.getvalue()
        if len(data) > MAX_MB * 1024 * 1024:
            st.error(f"الملف {len(data)/1048576:.1f}MB — الحد {MAX_MB}MB.")
        else:
            digest = hashlib.md5(data).hexdigest()
            if st.session_state.get("digest") != digest:
                reset()
                pages, warn = extract(data)
                if warn:
                    st.error(warn)
                recs = chunk(pages)
                if not recs:
                    st.error("لم يُستخرج نص كافٍ من هذا الملف.")
                else:
                    with st.spinner(f"جارٍ فهرسة {len(recs)} مقطعاً من {len(pages)} صفحة…"):
                        idx = DocIndex(recs, ce=getattr(retriever, "ce", None))
                    st.session_state.update(digest=digest, idx=idx, recs=recs,
                                            data=data, fname=up.name)
            if st.session_state.get("digest") == digest:
                recs = st.session_state.recs
                st.success(f"**{st.session_state.fname}** — {len(recs)} مقطعاً جاهزة للسؤال.")
                active_ret = st.session_state.idx
                active_by = {int(r["article_no"]): r for r in recs}
                refuse_t = st.slider(
                    "حساسية الرفض — أقل = يجيب أكثر ويخطئ أكثر",
                    0.30, 0.80, UPLOAD_REFUSE, 0.05,
                    help="مُعايَر على مستند واحد فقط. 0.30 غطّت 92% من الأسئلة "
                         "بدقة 84%؛ 0.50 غطّت 81% بدقة 87%. الحجب كان 100% عند الاثنتين.")
                warn_t = refuse_t + 0.20
                up_data = st.session_state.data
                ready = True


EXAMPLES = [
    "كم مدة الإشعار عن تسرب البيانات؟",
    "هل النظام ينطبق على استخدامي الشخصي لبيانات أصدقائي؟",
    "كيف تثبت الشركة إني وافقت على معالجة بياناتي؟",
]

if ready:
    if "q" not in st.session_state:
        st.session_state.q = ""

    if mode == "اللائحة التنفيذية":
        st.write("**أمثلة:**")
        for c, ex in zip(st.columns(len(EXAMPLES)), EXAMPLES):
            if c.button(ex, use_container_width=True):
                st.session_state.q = ex

    q = st.text_input("اكتب سؤالك", value=st.session_state.q,
                      placeholder="مثال: ما حقوق صاحب البيانات؟")
    go = st.button("اسأل", type="primary")

    if go and q.strip():
        t0 = time.time()
        with st.spinner("جارٍ البحث…"):
            st.session_state.res = answer(
                q.strip(), active_ret,
                allow_rewrite=(mode == "اللائحة التنفيذية"),
                refuse_below=refuse_t, warn_below=warn_t)
        st.session_state.secs = time.time() - t0

    if st.session_state.get("res"):
        res = st.session_state.res
        secs = st.session_state.secs

        colour, label = {
            "answer": ("#1a7f37", "ثقة عالية"),
            "warn":   ("#b26a00", "ثقة منخفضة"),
            "refuse": ("#b3261e", "خارج نطاق المستند"),
        }[res["action"]]

        st.markdown(
            f'<span class="badge" style="background:{colour}22;color:{colour}">'
            f'{label} · {res["score"]:.2f}</span>', unsafe_allow_html=True)

        if res.get("rewritten"):
            st.info(f'أُعيدت صياغة سؤالك للبحث: **{res["rewritten"]}**')

        st.markdown(f'<div class="answer">{res["text"]}</div>', unsafe_allow_html=True)

        if res.get("notice"):
            st.warning(res["notice"])

        if res["sources"]:
            st.markdown("#### " + ("المواد المعروضة على النموذج"
                                   if mode == "اللائحة التنفيذية"
                                   else "المقاطع المعروضة على النموذج"))
            for lab, no in res["sources"]:
                rec = active_by.get(int(no))
                pg = rec.get("page") if rec else None
                head = f"{lab}  (صفحة {pg})" if pg else lab
                with st.expander(head):
                    st.write(rec["text"] if rec else "—")
                    if pg:
                        if st.checkbox("📄 اعرض الصفحة من المستند", key=f"pg_{mode}_{no}"):
                            png = (page_png_up(st.session_state.digest, int(pg), up_data)
                                   if up_data else
                                   (page_png(int(pg)) if pdf_available() else None))
                            if png:
                                st.image(png, caption=f"صفحة {pg}")
                            else:
                                st.info("تعذّر عرض الصفحة.")
                    if rec and rec.get("source_url"):
                        st.markdown(f'<span class="meta">المصدر: {rec["source_url"]}</span>',
                                    unsafe_allow_html=True)

        st.markdown(f'<span class="meta">زمن الاستجابة: {secs:.1f} ثانية</span>',
                    unsafe_allow_html=True)

st.divider()
st.caption("مشروع بحثي — ليس استشارة قانونية. المرجع الرسمي هو نص اللائحة المنشور من سدايا.")
