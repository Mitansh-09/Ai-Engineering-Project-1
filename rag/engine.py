from sentence_transformers import SentenceTransformer
import numpy as np
import requests
import os
from dotenv import load_dotenv

load_dotenv()

_model = SentenceTransformer("all-MiniLM-L6-v2")
_chunks = []
_embeddings = None

def load_knowledge_base(file_paths):
    global _chunks, _embeddings
    all_text = ""
    for fname in file_paths:
        with open(fname) as f:
            all_text += f.read() + "\n\n"
    _chunks = chunk_text(all_text)
    _embeddings = _model.encode(_chunks)
    return len(_chunks)

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def retrieve(query, top_k=3):
    query_emb = _model.encode([query])[0]
    scores = np.dot(_embeddings, query_emb) / (
        np.linalg.norm(_embeddings, axis=1) * np.linalg.norm(query_emb)
    )
    top_idx = np.argsort(scores)[::-1][:top_k]
    return [{"text": _chunks[i], "score": float(scores[i])} for i in top_idx]

def generate_answer(query):
    results = retrieve(query, top_k=3)
    context = "\n\n".join([r["text"] for r in results])

    prompt = f"""Answer the question using ONLY the context below. If the context doesn't contain the answer, say "I don't know."

Context:
{context}

Question: {query}"""

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"},
        json={
            "model": "openrouter/free",
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    answer = response.json()["choices"][0]["message"]["content"]
    return {
        "answer": answer,
        "sources": results  # yeh "sources with answer" wala part hai
    }