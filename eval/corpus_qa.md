# Corpus QA — Executive Regulations

**Date:** 2026-09-09 · **Reviewed:** 5 of 38 articles (random, seed=7)

## Result
Article boundaries: 38/38 correct. No truncation, no merged articles,
no bleed into the following article. Numbering 1–38 with no gaps.

## Extraction issues found and resolved
| Issue | Detection | Fix |
|---|---|---|
| Arabic stored as Unicode presentation forms | 24,209 chars in FE70–FEFF; 0 regex matches for "المادة" | NFKC normalization → 76 matches |
| `sort=True` scrambles RTL block order | side-by-side comparison of both outputs | use default reading order |
| Bidi-displaced colon (`السادسة :عشرة`) | codepoint dump around failed matches | allow `[\s:]*` between ordinal tokens |
| Intra-word spacing from justification (`ا لمادة`) | printed the span between art. 16 and 19 | character-level flexible pattern |

## Known limitations
1. `title` is heuristic — accurate when the source uses a dash separator,
   otherwise truncated at 60 chars. Better approach: detect headings by
   span colour via `get_text("dict")`.
2. Punctuation position is unreliable (bidi). Word tokens are intact, so
   retrieval is not materially affected.

## Statistics
38 articles · shortest 111 chars · longest 2,837 · mean 1,006
