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
