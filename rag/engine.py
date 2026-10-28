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
    print("STATUS:", response.status_code)
    print("RESPONSE TYPE:", type(response.json()))
    data = response.json()
   

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
    answer = response.json()["choices"][0]["message"]["content"]
    return {"answer": answer, "sources": results}