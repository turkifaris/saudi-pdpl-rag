# Results

All figures produced by the scripts in `src/eval/`. Retrieval figures are measured on
the 75 in-scope questions of `eval/eval_set.json` unless stated otherwise.

## Corpus

| | |
|---|---|
| Articles extracted | 38 / 38 |
| Mean article length | 1,006 characters |
| Shortest / longest article | 111 / 2,837 characters |
| Manually reviewed | 20 articles |

## Question sets

| Set | In-scope | Out-of-scope | Types |
|---|---|---|---|
| `eval_set.json` | 75 | 10 | direct, procedural, paraphrase, multi, out-of-scope |
| `colloquial.json` | 14 | 8 | questions as a user types them |

## Retrieval

| System | Hit@1 | Hit@5 | Rec@5 | MRR | nDCG@10 |
|---|---|---|---|---|---|
| BM25 | 0.55 | 0.73 | 0.71 | 0.64 | 0.68 |
| Dense — bge-m3 | 0.79 | 0.99 | 0.97 | 0.86 | 0.88 |
| + cross-encoder rerank | 0.91 | 1.00 | 0.97 | 0.94 | 0.94 |

Hit@1 by question type:

| Type | n | BM25 | Dense | Rerank |
|---|---|---|---|---|
| direct | 25 | 0.72 | 0.80 | 0.96 |
| procedural | 23 | 0.61 | 0.78 | 0.87 |
| paraphrase | 17 | 0.35 | 0.65 | 0.82 |
| multi | 10 | 0.30 | 1.00 | 1.00 |

Median top-1 score, in-scope vs out-of-scope:

| System | in-scope | out-of-scope | separation | overlapping out-of-scope questions |
|---|---|---|---|---|
| BM25 | 6.49 | 4.50 | 1.4× | 2 / 10 |
| Dense | 0.64 | 0.55 | 1.2× | 0 / 10 |
| Rerank | 0.81 | 0.05 | 16× | 0 / 10 |

## Components measured and not shipped

| Component | Result | Shipped alternative |
|---|---|---|
| BM25 + dense RRF fusion | Hit@5 0.85 | Dense alone, 0.93 |
| gate-arabert (Arabic-specialised) | paraphrase 0.76 | bge-m3, 0.88 |
| arabic-triplet-matryoshka | paraphrase 0.71 | bge-m3, 0.88 |
| Derived article title in the embedded text | Hit@5 0.93 | Article text only, 0.97 |
| Always-on query rewriting | Hit@1 0.853 | Rewriting only below threshold, 0.907 |
| Orthographic folding of query and corpus | no failing question recovered; two regressed −0.11 and −0.32 | not used |

## Rejection policy

Refuse below 0.70, warn below 0.85. Query rewriting is invoked only when the first
retrieval scores below the refuse threshold.

| Question set | Coverage | Precision | Out-of-scope blocked | Answered and correct |
|---|---|---|---|---|
| Formal, 75 questions | 91% | 90% | 100% | 81% |
| Colloquial, 14 questions | 79% | 91% | 88% | 71% |

Threshold sweep, formal set:

| Threshold | Coverage | Precision | Out-of-scope blocked |
|---|---|---|---|
| 0.15 | 97% | 89% | 80% |
| 0.30 | 95% | 90% | 90% |
| 0.65 – 0.80 | 79% | 91% | 88% |
| 0.85 | 73% | 90% | 88% |

Behaviour is flat across 0.65–0.80.

## Generation

Three models, identical retrieved contexts, identical system prompt, temperature 0.1.
16 in-scope + 4 out-of-scope questions.

| Model | Cited | Cited correctly | Arabic purity | Out-of-scope refusal |
|---|---|---|---|---|
| command-r7b-arabic | 93% | 93% | 100% | 100% |
| qwen2.5:7b-instruct | 68% | 68% | 90% | 100% |
| ALLaM-7B-Instruct-preview | 43% | 43% | 100% | 100% |

Cited and cited-correctly are identical for every model: no model produced an incorrect
article number.

## Manual faithfulness review

20 answers from command-r7b-arabic, reviewed individually.

| | |
|---|---|
| Answer attempts | 15 |
| Fully supported by the cited article | 14 (93%) |
| Incomplete but correct | 1 (7%) |
| Hallucinations | 0 |
| False refusals | 0 |
| Correct refusals on out-of-scope questions | 4 / 4 |

## Uploaded-document mode

This corpus run through the generic upload path, scored against the same 85 questions.
Chunks mapped to articles by heading detection; 38 / 38 articles covered.

| Pipeline | Hit@1 | Hit@5 |
|---|---|---|
| Article-aware chunking | 0.907 | 1.000 |
| Generic chunking | 0.853 | 0.973 |

| Threshold | Coverage | Precision | Out-of-scope blocked |
|---|---|---|---|
| 0.30 | 92% | 84% | 100% |
| 0.50 (shipped default) | 81% | 87% | 100% |
| 0.70 | 73% | 87% | 100% |
| 0.90 | 49% | 92% | 100% |

## Regression test

`src/eval/regression.py` compares Hit@1, Hit@5 and the in/out-of-scope score medians for
the dense and rerank systems against `eval/baseline.json`, tolerance 0.01.
