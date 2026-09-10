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
