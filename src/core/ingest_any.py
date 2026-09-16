"""استخلاص وتقطيع أي PDF عربي — تقطيع عام بلا افتراض بنية."""
import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
import re, unicodedata

try:
    import pymupdf as fitz
except ImportError:
    import fitz

CHUNK = 900
OVERLAP = 150
MIN_CHARS_PER_PAGE = 40
BREAKS = re.compile(r"(?<=[.؟!])\s")


def _clean(t: str) -> str:
    t = unicodedata.normalize("NFKC", t)
    t = re.sub(r"^\s*\d{1,4}\s*$", " ", t, flags=re.M)
    return re.sub(r"\s+", " ", t).strip()


def extract(data: bytes):
    """يرجّع (صفحات, تحذير) — صفحات = [(رقم, نص)]"""
    doc = fitz.open(stream=data, filetype="pdf")
    pages = [(i + 1, _clean(doc[i].get_text())) for i in range(doc.page_count)]
    doc.close()
    total = sum(len(t) for _, t in pages)
    empty = sum(1 for _, t in pages if len(t) < MIN_CHARS_PER_PAGE)
    warn = None
    if total < 200:
        warn = "لا يوجد نص قابل للاستخلاص — المستند على الأرجح ممسوح ضوئياً ويحتاج OCR."
    elif empty > len(pages) * 0.4:
        warn = f"{empty} من {len(pages)} صفحة بلا نص — قد تكون صوراً."
    return pages, warn


def chunk(pages, size: int = CHUNK, overlap: int = OVERLAP, min_len: int = 150):
    """تقطيع بحجم ثابت مع تداخل، يحترم حدود الجمل، ويحفظ رقم الصفحة."""
    out = []
    for page_no, text in pages:
        if len(text) < MIN_CHARS_PER_PAGE:
            continue

        units = []
        for sent in BREAKS.split(text):
            sent = sent.strip()
            while len(sent) > size:
                units.append(sent[:size])
                sent = sent[size:]
            if sent:
                units.append(sent)

        buf = ""
        for u in units:
            if buf and len(buf) + 1 + len(u) > size:
                out.append([page_no, buf])
                buf = (buf[-overlap:] + " " + u).strip()
                while len(buf) > size:
                    out.append([page_no, buf[:size]])
                    buf = buf[size:].strip()
            else:
                buf = (buf + " " + u).strip() if buf else u
        if buf:
            out.append([page_no, buf])

    fwd = []
    for pg, tx in reversed(out):
        if (fwd and len(tx) < min_len and fwd[0][0] == pg
                and len(tx) + len(fwd[0][1]) + 1 <= size + overlap):
            fwd[0][1] = tx + " " + fwd[0][1]
        else:
            fwd.insert(0, [pg, tx])
    out = fwd

    merged = []
    for pg, tx in out:
        if (merged and len(tx) < min_len and merged[-1][0] == pg
                and len(merged[-1][1]) + len(tx) + 1 <= size + overlap):
            merged[-1][1] += " " + tx
        else:
            merged.append([pg, tx])

    return [{"id": f"chunk-{i:04d}", "article_no": i + 1,
             "article_label": f"مقطع {i + 1}", "page": pg, "text": tx,
             "doc": "مستند مرفوع", "source_url": ""}
            for i, (pg, tx) in enumerate(merged)]


if __name__ == "__main__":
    data = _p.Path("data/raw/pdpl_regulations.pdf").read_bytes()
    pages, warn = extract(data)
    print("الصفحات:", len(pages), "| تحذير:", warn or "لا شيء")
    ch = chunk(pages)
    lens = [len(c["text"]) for c in ch]
    print("المقاطع:", len(ch), "| أقصر:", min(lens), "| أطول:", max(lens),
          "| المتوسط:", sum(lens) // len(lens))
    print("\nمثال (مقطع 20):")
    c = ch[19]
    print(f"  صفحة {c['page']}: {c['text'][:200]}…")
