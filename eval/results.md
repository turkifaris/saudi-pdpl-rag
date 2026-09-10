# Retrieval Results

Eval set: 85 hand-labelled Arabic questions (75 in-scope, 10 out-of-scope)
Corpus: 38 articles, Executive Regulations of the Saudi PDPL

## Baseline — BM25 (lexical only, no models)

| Question type | n  | Hit@1 | Hit@5 | Rec@5 | MRR  | nDCG@10 |
|---------------|----|-------|-------|-------|------|---------|
| direct        | 25 | 0.72  | 0.88  | 0.88  | 0.80 | 0.84    |
| procedural    | 23 | 0.61  | 0.78  | 0.78  | 0.69 | 0.74    |
| paraphrase    | 17 | 0.35  | 0.53  | 0.53  | 0.45 | 0.51    |
| multi         | 10 | 0.30  | 0.60  | 0.42  | 0.43 | 0.41    |
| **overall**   | 75 | **0.55** | **0.73** | 0.71 | 0.64 | **0.68** |

### Findings
1. **0.35 gap between direct (0.88) and paraphrase (0.53) Hit@5.** Lexical
   retrieval cannot bridge vocabulary mismatch — the user writes "مسح",
   the law says "إتلاف". This motivates dense retrieval (week 3).
2. **Hit@1 0.55 vs Hit@5 0.73.** The correct article is usually retrieved
   but poorly ranked — a reranking problem, not a recall problem (week 4).
3. **multi: Hit@5 0.60 but Rec@5 0.42.** One gold article is found, not all.
   Structural limit of k=5 for questions spanning 6 articles.

### Out-of-scope separation
| | n | median top-1 score | mean |
|---|---|---|---|
| in-scope | 75 | 6.49 | 8.21 |
| out-of-scope | 10 | 4.50 | 4.64 |

Only 2/10 out-of-scope questions score above the in-scope median — a score
threshold is a viable first rejection mechanism, to be tuned in week 4.

## Dense retrieval — multilingual-e5-small

| Question type | n  | Hit@1 | Hit@5 | Rec@5 | MRR  | nDCG@10 |
|---------------|----|-------|-------|-------|------|---------|
| direct        | 25 | 0.80  | 0.92  | 0.92  | 0.86 | 0.89    |
| procedural    | 23 | 0.78  | 0.91  | 0.91  | 0.82 | 0.84    |
| paraphrase    | 17 | 0.29  | 0.76  | 0.76  | 0.47 | 0.57    |
| multi         | 10 | 0.80  | 0.90  | 0.70  | 0.83 | 0.80    |
| **overall**   | 75 | **0.68** | **0.88** | 0.85 | 0.76 | **0.79** |

### vs BM25 baseline
| metric | BM25 | dense | Δ |
|---|---|---|---|
| Hit@5 overall | 0.73 | 0.88 | **+0.15** |
| Hit@5 paraphrase | 0.53 | 0.76 | **+0.23** |
| Hit@5 multi | 0.60 | 0.90 | **+0.30** |
| out-of-scope above in-scope median | 2/10 | **0/10** | — |

### Key finding
Paraphrase Hit@1 *dropped* (0.35 → 0.29) while Hit@5 rose sharply
(0.53 → 0.76). Dense retrieval recovers the correct article far more often
but ranks it worse at position 1 — a reranking problem, not a recall one.

Score separation is cleaner (0/10 vs 2/10) but the margin is thin: cosine
scores compress into 0.84–0.86, versus BM25's 4.50–6.49. A raw-score
threshold is less robust for dense than the ordering suggests.
