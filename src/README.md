# Source map

Four folders by role. Everything imports flat (each script puts `src/` and its
subfolders on `sys.path`), so `from generate import answer` works from anywhere.
Run scripts from the repository root.

## `core/` — the running system
Imported by the app and by every evaluation script. This is the system the
reported numbers describe.

| File | Role |
|---|---|
| `embed.py` | loads the embedding model, encodes the corpus (also runnable to rebuild vectors) |
| `dense.py` | dense retrieval over cached embeddings |
| `retrieve.py` | BM25 baseline retrieval |
| `rerank.py` | cross-encoder reranking of the dense candidate pool |
| `rewrite.py` | colloquial → legal-register query rewriting (cascade rung 2) |
| `policy.py` | rejection policy: refuse below 0.70, warn below 0.85 |
| `generate.py` | end-to-end: retrieve → cascade → policy → grounded generation |
| `normalize.py` | Arabic normalisation + tokenisation for the **lexical** index only |
| `ordinals.py` | Arabic ordinal vocabulary and the bidi-tolerant heading regex |

## `pipeline/` — building the corpus
Run once, in this order, to rebuild `data/corpus.jsonl` from the source PDF.
`make_index.py` writes the human-readable article index in `eval/`.

## `eval/` — measurement
Everything that produces a number in `eval/results.md`.

| File | Role |
|---|---|
| `metrics.py` | shared scoring: Hit@1, Hit@5, Rec@5, MRR, nDCG, in/out-of-scope separation |
| `evaluate.py` | `python src/eval/evaluate.py [bm25\|dense\|rerank]` |
| `threshold.py` | sweeps the rejection threshold |
| `cascade.py` | simulates the rewrite cascade offline from cached scores |
| `eval_rw.py` · `eval_colloquial.py` | full evaluation with and without rewriting |
| `shootout.py` · `llm_shootout.py` | embedding and generation model comparisons |
| `build_contexts.py` | caches retrieved contexts so model comparisons are controlled |
| `rescore.py` | re-scores saved answers after a metric fix, without regenerating |
| `ablate_title.py` | the derived-title ablation |
| `errors.py` | lists the worst retrieval failures with gold vs retrieved |
| `review_faith.py` · `review_labels.py` · `label_colloquial.py` | manual review tooling |
| `fix_verdicts.py` | rule-based correction of mislabelled manual verdicts |
| `validate_eval.py` | sanity-checks the evaluation set |

## `archive/` — one-off diagnostics and rejected experiments
Kept deliberately as evidence, not wired into the running system.

- **Extraction diagnostics (week 1):** `inspect_encoding.py`, `inspect_text.py`,
  `find_headings.py`, `find_gaps.py`, `probe_gap.py`, `qa_sample.py`, `show.py` —
  the tools used to take article detection from 32/38 to 38/38.
- **Rejected components:** `hybrid.py` (BM25+dense RRF fusion),
  `arabic.py` + `embed_folded.py` + `fold_retrieve.py` + `probe_fold.py`
  (orthographic folding). Both were measured and not shipped; figures in `eval/results.md`.
- **Probes:** `probe.py`, `probe_rw.py` — the diagnostics that exposed the
  reranker's collapse on non-formal Arabic.
- `embedding_demo.py` — week-0 scratch.
