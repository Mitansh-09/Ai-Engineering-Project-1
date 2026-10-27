def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

# Load notes files as one knowledge base
all_text = ""
for fname in ["data/day1_notes.md", "data/day2_notes.md"]:
    with open(fname) as f:
        all_text += f.read() + "\n\n"

chunks = chunk_text(all_text)
print(f"Created {len(chunks)} chunks")
print(chunks[0])


from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(chunks)
print(embeddings.shape)


import numpy as np

def retrieve(query, chunks, embeddings, model, top_k=3):
    query_emb = model.encode([query])[0]
    scores = np.dot(embeddings, query_emb) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_emb)
    )
    top_idx = np.argsort(scores)[::-1][:top_k]
    return [(chunks[i], scores[i]) for i in top_idx]

# Test retrieval
results = retrieve("What does the --reload flag do?", chunks, embeddings, model)
for chunk, score in results:
    print(f"Score: {score:.3f}")
    print(chunk[:150])
    print("---")


import requests
import os
from dotenv import load_dotenv

load_dotenv()

def generate_answer(query, chunks, embeddings, model):
    results = retrieve(query, chunks, embeddings, model, top_k=3)
    context = "\n\n".join([chunk for chunk, score in results])

    prompt = f"""Answer the question using ONLY the context below. If the context doesn't contain the answer, say "I don't know."

Context:
{context}

Question: {query}"""

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        },
        json={
            "model": "openrouter/free",
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    return response.json()["choices"][0]["message"]["content"]

# Test 1: question with answer in notes
print("\n--- Test: answer exists ---")
print(generate_answer("What does the --reload flag do?", chunks, embeddings, model))

# Test 2: question with NO answer in notes
print("\n--- Test: answer does NOT exist ---")
print(generate_answer("What is Docker?", chunks, embeddings, model))

# Test 3: your own question
print("\n--- Test: your own question ---")
print(generate_answer("What does tool calling let the model do?", chunks, embeddings, model))