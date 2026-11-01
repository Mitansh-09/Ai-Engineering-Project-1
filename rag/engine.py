import numpy as np
import requests
import os
from dotenv import load_dotenv

load_dotenv()

_chunks = []
_embeddings = None

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def get_embedding(text):
    response = requests.post(
        url="https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction",
        headers={"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"},
        json={"inputs": text}
    )
    return response.json()

def load_knowledge_base(file_paths):
    global _chunks, _embeddings
    all_text = ""
    for fname in file_paths:
        with open(fname) as f:
            all_text += f.read() + "\n\n"
    _chunks = chunk_text(all_text)
    _embeddings = np.array([get_embedding(c) for c in _chunks])
    return len(_chunks)

def retrieve(query, top_k=3):
    query_emb = np.array(get_embedding(query))
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
    data = response.json()
    if "choices" not in data:
        return {"answer": f"ERROR: {data.get('error', {}).get('message', 'unknown error')}", "sources": results}
    answer = data["choices"][0]["message"]["content"]
    return {"answer": answer, "sources": results}


def rewrite_query(query, n=3):
    prompt = f"""Generate {n} different ways to ask this same question, to help with document search. Return ONLY the questions, one per line, no numbering.

Original question: {query}"""

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"},
        json={
            "model": "openrouter/free",
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    data = response.json()
    if "choices" not in data:
        return [query]
    text = data["choices"][0]["message"]["content"]
    variants = [line.strip() for line in text.split("\n") if line.strip()]
    return [query] + variants


def retrieve_multi_query(query, top_k=3):
    variants = rewrite_query(query)
    all_results = {}
    for v in variants:
        results = retrieve(v, top_k=top_k)
        for r in results:
            if r["text"] not in all_results or r["score"] > all_results[r["text"]]["score"]:
                all_results[r["text"]] = r
    sorted_results = sorted(all_results.values(), key=lambda x: x["score"], reverse=True)
    return sorted_results[:top_k]