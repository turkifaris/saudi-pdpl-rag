"""توحيد إملائي خفيف — للبحث فقط، لا للعرض ولا للاستشهاد."""
import re, unicodedata

_DIACRITICS = re.compile(r"[\u064B-\u0652\u0670\u0640]")
_ALEF       = re.compile(r"[أإآٱ]")
_AR_DIGITS  = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

def fold(t: str) -> str:
    t = unicodedata.normalize("NFKC", t)
    t = _DIACRITICS.sub("", t)
    t = _ALEF.sub("ا", t)
    t = (t.replace("ة", "ه").replace("ى", "ي")
           .replace("ؤ", "و").replace("ئ", "ي"))
    t = t.translate(_AR_DIGITS)
    return re.sub(r"\s+", " ", t).strip()

if __name__ == "__main__":
    PAIRS = [("الموافقه", "الموافقة"), ("معالجه", "معالجة"),
             ("البينات", "البيانات"), ("الأثر", "الاثر"),
             ("المادة ٦", "المادة 6")]
    for a, b in PAIRS:
        ok = "تطابقا ✅" if fold(a) == fold(b) else "لم يتطابقا ❌"
        print(f"{a:>12} → {fold(a):<12} | {b:>12} → {fold(b):<12} {ok}")
