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
- TODO week 6: re-verify 4 eval items (personal-use phrasing, art 17 vs 36, المصلحة الحيوية scope, 2 borderline out_of_scope)
- Title ablation (week 3 day 5): dropping the derived title from the embedded
  text raised Hit@5 0.93 -> 0.97. Root cause traced to week-1 title heuristic
  duplicating the article opening. Title retained for display only.
- Generation layer live. Example of correct behaviour: "كم مدة الإشعار عن
  تسرب البيانات؟" -> 0.983 -> cites المادة 24, states 72 hours, ignores the
  two irrelevant articles also passed in context.
- Example of a false refusal (one of the measured 6/68): "أبي أمسح حسابي وكل
  شي عني" -> 0.009 -> refused, though Art. 8 answers it. Root cause: the word
  «حساب» does not exist anywhere in the Regulations — a vocabulary gap wider
  than synonymy. Candidate v2 fix: query rewriting (colloquial -> legal register)
  before retrieval.

## Week 4 — decisions and rejected paths

- Two "false refusal" metrics exist in this project and must not be conflated:
  1. **Retrieval-layer** (week 3): the score threshold suppresses a question whose gold
     article was retrievable. Measured 6/68. The «حساب» example above is this kind.
  2. **Generation-layer** (week 4): the model answers «لا تتضمن» although the gold
     article was in its context. Measured **0/20**.
  Different causes, different fixes. Always state which one a figure refers to.

- **Generation model: `command-r7b-arabic` selected.** Identical contexts, identical
  system prompt, identical temperature (0.1) — only the model varied. 93% citation,
  93% citation accuracy, 100% Arabic purity, 100% out-of-scope refusal. qwen2.5:7b
  reaches 90% Arabic purity, i.e. 1 answer in 10 leaks Latin or CJK characters —
  disqualifying for an Arabic legal assistant regardless of its other scores.
  **Licence is non-commercial (CC-BY-NC).** Must be stated in the README; a commercial
  deployment would need a different generator.

- **Rejected: hybrid BM25 + dense with RRF.** Hit@5 0.85 vs 0.93 for dense alone. RRF
  ranks by position, not by score, so it discarded the magnitude the rejection
  threshold depends on — the confidence signal collapsed. Weighted fusion
  (w_bm25=0.3) did not recover it. Kept as a documented negative result: the standard
  recipe lost to the simpler component on this corpus.

- **Rejected: Arabic-specialised embeddings.** gate-arabert scored 0.76 on paraphrase
  questions vs 0.88 for multilingual bge-m3. "Arabic-specialised" did not imply better
  on Arabic here. It remains the deployment fallback: 541MB vs 2.2GB at equal Hit@5.

- **Largest single retrieval gain came from removing a component**, not adding one:
  dropping the derived title from the embedded text (week 3 day 5). The title heuristic
  was already flagged as a limitation in week 1; the limitation log paid for itself.

- **Measurement bug: the citation detector.** Matched `المادة\s+` only, missing every
  clitic-prefixed citation (للمادة / بالمادة / والمادة). Depressed every reported
  citation rate by 5–12 points for two weeks. Found by manual review, not by a test.
  Fixed in `src/rescore.py` + `src/fix_verdicts.py`; rankings unchanged.
  **Rule adopted: the evaluation harness needs its own evaluation.**

- **Annotation error: criterion drift.** During manual review, verdict 5 ("false
  refusal") was pressed whenever the ⚠️ *no citation* flag appeared, rather than when
  the stated rule held. 6 of 20 verdicts were affected. Two root causes: (a) the tool
  renders two different warnings with the same symbol; (b) a detector signal was being
  read as a verdict. Corrected by rule, not by memory, each change carrying a `note`.
  **Week 5 fix: distinct colours for "low confidence" and "no citation" in the UI.**

- **Reranker cost, unresolved for week 5.** bge-reranker-v2-m3 adds 2.2GB and ~2.8s per
  query on MPS, 10–30s on CPU. Free hosting is CPU-only and memory-constrained.
  Open decision: ship dense-only (0.91 Hit@1, fast) or dense+rerank (higher accuracy,
  unusable latency on free tier).

- **Lookup-by-article-number is out of scope (deliberate).** "ما هي المادة ٦؟" fails:
  the corpus spells article numbers as Arabic ordinals ("السادسة"), and the question
  carries no semantic content for the reranker to match, so it scores near zero and is
  refused. Diagnosed as a *query-type* mismatch, not a retrieval failure — a navigational
  query needs a direct-lookup route, not semantic search. A route was designed
  (regex → article id → fetch, bypassing retrieval) and **deliberately not shipped** in
  v1 to keep the scope on semantic Q&A. Candidate for v2.

- **Two evaluation sets, measuring different things.** `eval_set.json` (85 questions,
  written while reading the Regulations) measures retrieval quality. `colloquial.json`
  (22 questions, written as a real user types) measures whether the system is *usable*.
  The second was built only in week 5, after using the UI exposed failures no metric had
  caught. Every finding of week 5 day 2 came from it, not from the 85.
- **100% out-of-scope blocking is not achievable on the colloquial set** (max 7/8), and
  not because the threshold is wrong — the single leak scores 0.931. Documented rather
  than tuned away.

- **Rejected: orthographic folding of query and corpus** (week 5, day 2). Free-spelling
  questions ("الموافقه", "معالجه") do not match the corpus spelling, so a folded index
  was built (ة→ه, أ/إ/آ→ا, ى→ي, diacritics stripped) and wired as a cheap middle rung of
  the cascade, before the expensive LLM rewrite. **Measured and rejected**: none of the
  three failing questions crossed the 0.70 threshold (best gain +0.003), and two got
  materially worse (−0.113, −0.324). bge-m3 already normalises these variants in its own
  tokenizer — it was trained on unnormalised web Arabic — so folding adds nothing, and
  folding the *corpus* moves it away from the distribution the model was trained on.
  This re-confirms by measurement the rule adopted in week 2 from reasoning alone:
  **normalise for the lexical index only, never for dense models.**
  The experiment is kept and is reproducible: `src/arabic.py`, `src/fold_retrieve.py`,
  `python src/probe_fold.py`. Not wired into `generate.py`.

- **Kept from that work:** `get_model()` is now `@lru_cache`d, so building a second
  retriever no longer loads a second 2.2GB copy of the embedding model.
