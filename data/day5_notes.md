# Day 5 — RAG wrapped in FastAPI

## What changed
Moved RAG logic (chunking, embeddings, retrieval, generation) out of a
standalone script into rag/engine.py as reusable functions. main.py now
exposes a POST /ask endpoint that any client can call over HTTP.

## Key additions
- load_knowledge_base() runs once at FastAPI startup (not per-request) —
  loading the embedding model and encoding chunks is slow, so doing it
  once avoids redoing that work on every API call.
- generate_answer() now returns both the answer AND the sources
  (retrieved chunks + similarity scores), not just a string. This lets
  the caller see WHY the model gave that answer, which matters for
  trust in a real application.

## Needed a Python package structure
Had to add rag/__init__.py (empty file) to make Python treat the rag/
folder as an importable package — without it, `from rag.engine import ...`
fails with ModuleNotFoundError.

## Tested via /docs
Sent a POST request to /ask with "What does tool calling let the model
do?" — got a correct answer plus 3 ranked sources with similarity
scores (0.63, 0.62, 0.50). The top-scored chunk was the most directly
relevant one.

## Key takeaway
A script that works top-to-bottom is not the same as an API. Wrapping
it in FastAPI means the knowledge base loads once and stays in memory,
while any number of requests can query it — this is the shape every
real RAG application takes.