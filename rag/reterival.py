def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

# Load both your notes files as one knowledge base
all_text = ""
for fname in ["data/day1_notes.txt", "data/day2_notes.txt"]:
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

# Test with questions you know the answer to from your own notes
results = retrieve("What does the --reload flag do?", chunks, embeddings, model)
for chunk, score in results:
    print(f"Score: {score:.3f}")
    print(chunk[:150])
    print("---")