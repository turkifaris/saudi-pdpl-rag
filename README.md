# Saudi PDPL RAG Assistant

An Arabic retrieval-augmented generation system that answers questions about
Saudi Arabia's Personal Data Protection Law (PDPL) and its executive
regulations, citing the exact article number and official source.

**Status:** in development — week 0 (environment setup)

## Why
General-purpose LLMs hallucinate article numbers in legal text, and
organizations handling sensitive documents cannot send them to external APIs.
This system is grounded in a controlled corpus and runs entirely locally.

## Stack
Python 3.11 · PyTorch (MPS) · sentence-transformers · BM25 + dense hybrid
retrieval · Ollama for local generation · Streamlit

## Results
_Evaluation table coming in week 3._

## Corpus
| Metric | Value |
|---|---|
| Source documents | 1 (Executive Regulations) |
| Articles | 38 / 38 |
| Mean article length | 1,006 chars |
| Manual QA | 5 articles reviewed — see `eval/corpus_qa.md` |

## Corpus
| Metric | Value |
|---|---|
| Source | Executive Regulations of the Saudi PDPL |
| Articles extracted | 38 / 38 |
| Mean article length | 1,006 chars |
| Manual QA | 20 articles reviewed — `eval/corpus_qa.md` |

Extraction required solving four Arabic-specific problems: Unicode
presentation forms, RTL block ordering, bidi-displaced punctuation, and
intra-word spacing from PDF justification. Article detection improved
from 32/38 to 38/38 as each was diagnosed and fixed.

## Results
| System | Hit@5 | nDCG@10 |
|---|---|---|
| BM25 baseline | 0.73 | 0.68 |

Full breakdown by question type in `eval/results.md`.
