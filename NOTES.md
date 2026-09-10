- Deployment deferred to week 5. HF Spaces free tier is now Static-only; plan to use Streamlit Community Cloud.
- Title extraction is heuristic (bidi displaces the colon separating heading from body). Better approach: use PyMuPDF get_text('dict') and detect headings by span COLOR — they are orange in the source PDF. Deferred.
- BM25 baseline failure modes observed:
  1. synonym blindness: query "حذف" misses article 8 "إتلاف"
  2. Arabic clitics: "بجهة" != "جهة" (proclitic attached to token)
  3. no rejection threshold: out-of-scope query returned score 4.01
  4. high-frequency domain terms ("جهة التحكم", 35/38 articles) carry no signal
- Eval set v1: 85 questions, 37/38 articles (art 38 = publication clause, excluded by design).
- Drafting: ~30 AI-drafted then human-verified; rest human-authored. All gold labels human-assigned.
- Limitation: direct/procedural phrasing is more formal than real users; paraphrase items (17) carry realistic phrasing.
