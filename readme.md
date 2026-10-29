# RAG API — Notes Q&A System

A Retrieval-Augmented Generation API that answers questions using your own documents, with cited sources.

**Live demo:** https://ai-engineering-project-1-om4n.onrender.com/docs
(Free tier — first request may take 30-50s to wake up)

## What it does
- Chunks markdown documents and converts them to embeddings
- Retrieves the most relevant chunks for a question using cosine similarity
- Generates answers using an LLM, constrained to only use retrieved context
- Returns both the answer and its sources (with similarity scores)
- Correctly says "I don't know" when the answer isn't in the knowledge base

## Stack
- FastAPI (API layer)
- HuggingFace Inference Router (embeddings — chosen to fit free-tier memory limits)
- OpenRouter (LLM generation)
- NumPy (cosine similarity, hand-written — not a vector DB library)

## Architecture
1. `/ask` endpoint receives a question
2. Question is embedded via HuggingFace API
3. Cosine similarity ranks stored document chunks
4. Top-3 chunks become context for the LLM
5. LLM answers using ONLY that context

## Try it
POST to `/ask` with a `query` parameter at `/docs`.

## What I'd improve with more time
- Swap hand-written cosine similarity for a real vector DB (Qdrant/FAISS) at scale
- Add evals (Ragas) to measure retrieval quality numerically
- Cache embeddings instead of recomputing on every startup