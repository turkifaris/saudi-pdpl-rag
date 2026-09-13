# Saudi PDPL RAG Assistant

An Arabic retrieval-augmented generation system that answers questions about
Saudi Arabia's Personal Data Protection Law (PDPL) and its executive
regulations, citing the exact article number and official source.

**Status:** week 4 complete — retrieval, rejection policy and grounded generation
evaluated. UI and deployment in week 5.

## Why
General-purpose LLMs hallucinate article numbers in legal text, and organizations
handling sensitive documents cannot send them to external APIs. This system is
grounded in a controlled corpus and runs entirely locally.

## Stack
Python 3.11 · PyTorch (MPS) · sentence-transformers · dense retrieval (bge-m3) ·
Ollama for local generation · Streamlit

## Corpus
| Metric | Value |
|---|---|
| Source | Executive Regulations of the Saudi PDPL (SDAIA) |
| Articles extracted | 38 / 38 |
| Mean article length | 1,006 chars |
| Manual QA | 20 articles reviewed — `eval/corpus_qa.md` |

Extraction required solving four Arabic-specific problems: Unicode presentation forms,
RTL block ordering, bidi-displaced punctuation, and intra-word spacing from PDF
justification. Article detection improved from 32/38 to 38/38 as each was diagnosed.

## Retrieval results
| System | Hit@1 | Hit@5 | paraphrase | nDCG@10 |
|---|---|---|---|---|
| BM25 baseline | 0.55 | 0.73 | 0.53 | 0.68 |
| + dense (e5-small) | 0.68 | 0.88 | 0.76 | 0.79 |
| + bge-m3 | 0.80 | 0.93 | 0.88 | 0.86 |
| **− derived title** | 0.79 | **0.97** | **0.94** | **0.88** |

Evaluated on 85 hand-labelled Arabic questions across five question types.

- Hybrid BM25+dense fusion was tested and **rejected** (Hit@5 0.85 < 0.93): RRF ranks by
  position, destroying the score magnitude the rejection threshold depends on.
- Arabic-specialised embeddings were benchmarked and **lost** to multilingual bge-m3
  (paraphrase 0.76 vs 0.88).
- The largest single gain came from *removing* a component, not adding one.

## Rejection policy
Two thresholds on the top-1 retrieval score: refuse below 0.08, warn below 0.30.
96% precision on confidently-answered questions. An out-of-scope question is answered
with an explicit refusal rather than a guess.

## Generation results
Identical contexts, identical system prompt, identical temperature (0.1) — only the
model varies. 16 in-scope + 4 out-of-scope questions.

| Model | cited | cited correctly | Arabic purity | out-of-scope refusal |
|---|---|---|---|---|
| **command-r7b-arabic** | **93%** | **93%** | 100% | 100% |
| qwen2.5:7b-instruct | 68% | 68% | 90% | 100% |
| ALLaM-7B-Instruct-preview | 43% | 43% | 100% | 100% |

**Zero incorrect citations across all three models** — `cited` equals `cited correctly`
everywhere. The failure mode is omission, never fabrication: no model invented an
article number. For a legal assistant this is the property that matters most.

### Manual faithfulness review
20 answers from the selected model, reviewed one by one (`eval/faithfulness.md`):

| Metric | Value |
|---|---|
| Fully supported by the cited article | 93% |
| **Hallucinations** | **0** |
| False refusals (gold article was in context) | **0** |
| Correct refusals on out-of-scope questions | 4 / 4 |

The review also exposed a bug in the *evaluation harness*: the citation detector matched
`المادة` only and missed clitic-prefixed forms (للمادة / بالمادة / والمادة), depressing
every reported citation rate by 5–12 points. Fixed and rescored; the model ranking did
not change. See `eval/results.md`.

## Licence note
`command-r7b-arabic` is released under **CC-BY-NC (non-commercial)**. It is used here for
a research and portfolio project. A commercial deployment would require substituting a
differently-licensed generator; the retrieval stack is unaffected.

## Known limitations
- Corpus is the Executive Regulations only. The Law itself is a scanned PDF and needs
  OCR — deferred to v2.
- Only 10 out-of-scope questions, so the rejection threshold is tuned on a coarse sample.
- `multi` questions: retrieval surfaces all three articles, generation covers 1–2.
- Colloquial phrasing with no lexical overlap with the legal register still fails
  (e.g. «حساب», a word absent from the Regulations). Candidate v2 fix: query rewriting.
- Manual review by a single annotator; no inter-annotator agreement measured.

## Documentation
- `eval/results.md` — full methodology, ablations, rejected approaches
- `eval/faithfulness.md` — manual review protocol and results
- `NOTES.md` — decision log, including paths that were tried and abandoned
