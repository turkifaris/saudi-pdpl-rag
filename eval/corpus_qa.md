# Corpus QA — Executive Regulations

**Date:** 2026-09-09 · **Reviewed:** 20 of 38 articles (random, seed=7)

## Result
Article boundaries correct in 20/20. No truncation at the start, no bleed
into the following article, no merged articles. Numbering 1–38, no gaps.

## Extraction problems found and fixed
| Problem | How it was detected | Fix |
|---|---|---|
| Arabic stored as Unicode presentation forms | 24,209 chars in FE70–FEFF; 0 regex matches for "المادة" | NFKC normalization → 76 matches |
| `sort=True` scrambles RTL block order | side-by-side diff of both extraction modes | keep default reading order |
| Bidi-displaced colon (`السادسة :عشرة`) | codepoint dump around failing matches | allow `[\s:]*` between ordinal tokens |
| Intra-word spacing from justification (`ا لمادة`) | printed the raw span between art. 16 and 19 | character-level flexible pattern |

Detection rate improved 32 → 35 → 36 → 38 of 38 as each was fixed.

## Known limitations
1. `title` is heuristic: exact when the source separates heading from body
   with a dash, truncated at 60 chars otherwise (6 of 20 sampled).
   Planned fix: detect headings by span colour via `get_text("dict")`.
2. Punctuation position is unreliable (bidi). Word tokens are intact, so
   lexical and dense retrieval are not materially affected.
3. Article 14 is unusually short (190 chars) — flagged for source check.

## Statistics
38 articles · shortest 190 · longest 2,837 · mean 1,006 chars
