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

## Hybrid (RRF) — rejected

| System | Hit@1 | Hit@5 | nDCG@10 |
|---|---|---|---|
| BM25 | 0.55 | 0.73 | 0.68 |
| dense (e5-small) | 0.68 | **0.88** | **0.79** |
| hybrid RRF (1:1) | 0.64 | 0.84 | 0.76 |
| hybrid RRF (bm25 0.3 : dense 1.0) | 0.68 | 0.85 | 0.78 |

**Decision: BM25 dropped from the pipeline.**

Fusion was tested because hybrid retrieval is the industry default. On this
corpus it hurt: Hit@5 0.88 → 0.85 even after down-weighting BM25 to 0.3.

Where it helped: first-position ranking (direct Hit@1 0.80 → 0.84,
paraphrase Hit@1 0.29 → 0.35) — BM25 catches the literal token the dense
model blurs.

Where it broke: multi-article questions (Hit@5 0.90 → 0.80). Fusing a
diffuse lexical ranking pushes correct articles out of the top-5 for
questions whose answer spans 6 articles.

It also destroys the confidence signal: RRF scores are rank-based, so
in-scope and out-of-scope both sit at 0.02–0.03 and out-of-scope overlap
returns to 2/10 (dense alone: 0/10).

Likely cause: 38 documents give BM25 too little to discriminate on, and the
two systems are 0.15 apart in strength — far from the near-parity fusion
assumes.

## Embedding model shootout

Same corpus, same 85 questions, same metrics. Only the model changes.

| Model | dim | size | Hit@1 | Hit@5 | paraphrase | multi | nDCG | out-of-scope |
|---|---|---|---|---|---|---|---|---|
| multilingual-e5-small | 384 | 470MB | 0.68 | 0.88 | 0.76 | 0.90 | 0.79 | 0/10 |
| **BAAI/bge-m3** | 1024 | 2.2GB | **0.80** | **0.93** | **0.88** | 1.00 | **0.86** | 0/10 |
| Arabic-Triplet-Matryoshka-V2 | 768 | 541MB | 0.69 | 0.92 | 0.76 | 1.00 | 0.81 | 1/10 |
| GATE-AraBert-v1 | 768 | 541MB | 0.71 | 0.93 | 0.76 | 1.00 | 0.81 | 1/10 |

**Winner: bge-m3.**

### The hypothesis was wrong
The project assumed Arabic-specialised embeddings would beat general
multilingual ones on Arabic legal text. They did not: both Arabic models
trail bge-m3 by 0.12 on paraphrase Hit@5 and 0.09–0.11 on Hit@1.

The Arabic-Triplet model card states the limitation directly — it "may not
perform optimally on highly technical or domain-specific" content. Arabic
regulatory prose is exactly that. Language specialisation is not domain
specialisation, and bge-m3's far larger and more formal training corpus
appears to outweigh it here.

### Deployment tension (unresolved, week 5)
GATE-AraBert-v1 matches bge-m3 on Hit@5 (0.93) at **a quarter of the size**
(541MB vs 2.2GB), losing only on paraphrase and first-position ranking.
Free-tier hosting is memory-constrained, so the production model may not be
the benchmark winner.

## Ablation: article title in the embedded text

| Embedded text | Hit@1 | Hit@5 | paraphrase | nDCG@10 |
|---|---|---|---|---|
| title + text | 0.80 | 0.93 | 0.88 | 0.86 |
| **text only** | 0.79 | **0.97** | **0.94** | **0.88** |

**Removing the title improved retrieval.** Hit@5 +0.04, paraphrase +0.06.

### How this was found
Error analysis on the 5 remaining top-5 failures showed 3 of them targeting
just two articles (21 and 22). Article 21 was one of the six whose extracted
`title` was truncated mid-word at 60 characters — a limitation documented
during corpus construction in week 1.

### Why it hurt
The `title` field is derived by slicing the first ~60 characters of the
article body. Concatenating `title + text` therefore duplicates each
article's opening twice, biasing the vector toward the first sentence and,
for the six truncated cases, injecting a mid-word fragment as noise.

The fix costs nothing and removes a component rather than adding one — the
truncated-title limitation is now moot for retrieval, though `title` is
still used for display in results.

## Cross-encoder reranking

Two-stage: bge-m3 retrieves top-20, BAAI/bge-reranker-v2-m3 reorders to top-5.

| Metric | dense only | + reranker | Δ |
|---|---|---|---|
| Hit@1 | 0.79 | **0.88** | +0.09 |
| Hit@5 | 0.97 | 0.97 | 0.00 |
| MRR | 0.86 | **0.92** | +0.06 |
| nDCG@10 | 0.88 | **0.93** | +0.05 |
| paraphrase Hit@1 | 0.65 | **0.76** | +0.11 |

Hit@5 is unchanged by construction — a reranker reorders candidates, it
cannot retrieve new ones. Its entire contribution is ordering.

### Unplanned benefit: calibrated scores
| | in-scope median | out-of-scope median | gap |
|---|---|---|---|
| dense (cosine) | 0.64 | 0.55 | 0.09 |
| reranker | 0.81 | **0.05** | **0.76** |

Cosine similarity between any two Arabic texts compresses into a narrow
band, making a rejection threshold fragile. The cross-encoder is trained to
score relevance directly, so its output separates in-scope from
out-of-scope by 8x the margin. The reranker was added to fix ranking; it
also made the week-4 rejection threshold tractable.

### Cost
Reranking runs a full forward pass per (query, candidate) pair at query
time — nothing can be precomputed. Latency measured separately; this is the
main deployment trade-off for week 5.

### Latency (85 questions, M5 Air, MPS)
| System | total | per query |
|---|---|---|
| dense only | 12.0s | ~0.07s |
| + reranker | 249.5s | ~2.8s |

~40x slower per query. The reranker runs 20 full forward passes of a 2.2GB
cross-encoder per question (1,700 total); nothing can be precomputed because
the query is half of every input. CPU utilisation reads 4% because the work
is on the GPU — wall-clock is the only meaningful measure here.

On CPU-only free hosting this becomes 10-30s per query. Week-5 options:
drop the reranker (-0.09 Hit@1), shrink `pool` from 20 to 5, or use a
smaller cross-encoder.

## After label corrections

Two incomplete gold labels were corrected (see `label_fixes.md`). The system
was not modified — only the measurement.

| Metric | before | after | Δ |
|---|---|---|---|
| Hit@1 | 0.88 | **0.91** | +0.03 |
| Hit@5 | 0.97 | **1.00** | +0.03 |
| nDCG@10 | 0.93 | 0.94 | +0.01 |
| paraphrase Hit@1 | 0.76 | 0.82 | +0.06 |

Both figures are reported; the gain is measurement accuracy, not system
improvement.

### Reading Hit@5 = 1.00 honestly
The corpus is 38 articles, so returning the top 5 exposes **13% of the entire
corpus** per query. Random selection alone scores 0.13 at k=5. A perfect
Hit@5 on a corpus this small is expected of a strong retriever and is not
comparable to Hit@5 on a large collection.

**Hit@1 = 0.91 is the meaningful figure** — one correct article out of 38
(2.6% by chance).

### Remaining failures at k=1
| Question | Cause |
|---|---|
| q027 | Art. 22 not surfaced (top-1 score 0.009) |
| q037 | Art. 12 not surfaced (top-1 score 0.005) |

Both score near zero, so the rejection threshold suppresses them: the system
abstains rather than answering wrongly.

## Generation model comparison

Identical retrieved contexts, identical system prompt, identical temperature
(0.1). 30 questions (20 in-scope, 10 out-of-scope); only the model varies.

| Model | cited | cited correctly | refusal | Arabic purity | avg chars | secs |
|---|---|---|---|---|---|---|
| qwen2.5:7b-instruct | 56% | 56% | 100% | **90%** | 95 | 102 |
| **command-r7b-arabic** | **88%** | **88%** | 100% | 100% | 180 | 168 |
| ALLaM-7B-Instruct-preview | 31% | 31% | 100% | 100% | 162 | 88 |

**Winner: command-r7b-arabic.**

### Findings
1. **qwen2.5 language drift, quantified.** 90% Arabic purity means 1 in 10
   answers contains Latin or CJK characters. This was observed anecdotally in
   week 0 and is now measured. Both Arabic-tuned models score 100%.
2. **ALLaM's failure is instruction-following, not knowledge.** Its citation
   rate equals its citation accuracy (31% = 31%): when it cites, it is always
   right — it simply omits the citation in 69% of answers.
3. **All three refused 100% of out-of-scope questions.** A well-constrained
   prompt compensates for model weakness on compliance tasks.

### Caveats
- One prompt for all three. Fair in holding the variable constant, but each
  model may respond better to a different instruction style; ALLaM was not
  prompt-tuned.
- `ALLaM-7B-Instruct-preview` is a preview release, not the final model.
- n = 20 answered questions per model. The 88% vs 31% gap is large, but the
  sample is small.

The honest claim is: *under an identical prompt, ALLaM-preview omitted the
required citation in 69% of answers* — not that the model is weak.
