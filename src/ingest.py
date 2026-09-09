"""Extract raw text from source PDFs."""
import pymupdf
from pathlib import Path

RAW = Path("data/raw")
OUT = Path("data/interim")
OUT.mkdir(parents=True, exist_ok=True)


def extract(pdf_path: Path, sort: bool) -> str:
    doc = pymupdf.open(pdf_path)
    parts = []
    for i, page in enumerate(doc, start=1):
        parts.append(f"\n<<<PAGE {i}>>>\n")
        parts.append(page.get_text("text", sort=sort))
    doc.close()
    return "".join(parts)


if __name__ == "__main__":
    src = RAW / "pdpl_regulations.pdf"

    for sort in (False, True):
        text = extract(src, sort=sort)
        name = "regulations_sorted.txt" if sort else "regulations_plain.txt"
        (OUT / name).write_text(text, encoding="utf-8")
        print(f"{name:28} {len(text):>7} حرف")
