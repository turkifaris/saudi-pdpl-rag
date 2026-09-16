"""عرض صفحة من المستند الأصلي، مع تظليل نص المادة إن أمكن."""
import sys as _s, pathlib as _p; _SRC = _p.Path(__file__).resolve().parents[1]; _s.path[:0] = [str(_SRC)] + [str(d) for d in _SRC.iterdir() if d.is_dir()]
import re

try:
    import pymupdf as fitz
except ImportError:
    import fitz

ROOT = _p.Path(__file__).resolve().parents[2]
PDF = ROOT / "data" / "raw" / "pdpl_regulations.pdf"


def available() -> bool:
    return PDF.exists()


def _candidates(text: str):
    """مقتطفات نجرّب البحث عنها، من الأطول للأقصر."""
    words = text.split()
    for n in (12, 8, 5, 3):
        if len(words) >= n:
            yield " ".join(words[:n])


def render(page_no: int, highlight: str = "", dpi: int = 130):
    """يرجّع (صورة PNG بايت, هل نجح التظليل)."""
    if not PDF.exists():
        return None, False
    doc = fitz.open(PDF)
    if not (1 <= page_no <= doc.page_count):
        doc.close()
        return None, False
    page = doc[page_no - 1]

    found = False
    if highlight:
        for snip in _candidates(highlight):
            rects = page.search_for(snip)
            if rects:
                for r in rects:
                    page.add_highlight_annot(r)
                found = True
                break

    pix = page.get_pixmap(dpi=dpi)
    png = pix.tobytes("png")
    doc.close()
    return png, found


def render_from(data: bytes, page_no: int, dpi: int = 130):
    """عرض صفحة من بايتات PDF مرفوع."""
    doc = fitz.open(stream=data, filetype="pdf")
    if not (1 <= page_no <= doc.page_count):
        doc.close()
        return None
    png = doc[page_no - 1].get_pixmap(dpi=dpi).tobytes("png")
    doc.close()
    return png
