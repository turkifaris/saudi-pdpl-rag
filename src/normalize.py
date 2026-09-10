"""Arabic normalization for the SEARCH INDEX ONLY.

The stored article text keeps its official orthography. This module
produces a separate, normalized form used to build the index and to
process incoming queries — both sides must pass through it identically.
"""
import re
import unicodedata

TATWEEL = "\u0640"
DIACRITICS = re.compile(r"[\u064B-\u0652\u0670]")
ALEF = re.compile("[إأآٱا]")
PUNCT = re.compile(r"[^\w\s]", re.UNICODE)
DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

STOPWORDS = {
    "في", "من", "على", "الى", "إلى", "عن", "مع", "او", "أو", "و", "ثم",
    "التي", "الذي", "التى", "الذى", "هذا", "هذه", "ذلك", "تلك", "ما",
    "لا", "ان", "أن", "إن", "كان", "يكون", "تكون", "قد", "كل", "بعد",
    "عند", "غير", "بما", "به", "بها", "لها", "له", "هو", "هي", "اي", "أي",
}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(DIGITS)
    text = text.replace(TATWEEL, "")
    text = DIACRITICS.sub("", text)
    text = ALEF.sub("ا", text)
    text = text.replace("ى", "ي").replace("ة", "ه").replace("ؤ", "و").replace("ئ", "ي")
    text = PUNCT.sub(" ", text)
    return " ".join(text.split())


# قائمة الوقف تمر بنفس التطبيع، وإلا لن تتطابق أبداً
STOPWORDS = {normalize(w) for w in STOPWORDS}


def tokenize(text: str, drop_stopwords: bool = True) -> list[str]:
    toks = normalize(text).split()
    if drop_stopwords:
        toks = [t for t in toks if t not in STOPWORDS]
    return toks


if __name__ == "__main__":
    samples = [
        "الحق فى الوصول إلى البيانات الشخصية",
        "الحقّ في الوصـول الى البيانات الشخصية",
        "ما هي إجراءات الإشعار عن التسرّب؟",
    ]
    for s in samples:
        print("قبل :", s)
        print("بعد :", normalize(s))
        print("رموز:", tokenize(s))
        print()
