# Day 3 — RAG Basics (Retrieval)

RAG stands for Retrieval-Augmented Generation. Instead of relying only on what the LLM already knows, RAG retrieves relevant information from your own documents first, then gives that information to the LLM along with the question, so it can answer using real, specific data.

## Chunking
Large documents cannot be searched effectively as one block, so they are split into smaller pieces called chunks. I used a chunk size of 500 characters with 50 characters of overlap. The overlap exists so that information near the boundary of one chunk is not lost — it appears partially in both the current and next chunk.

**Problem I saw:** a 500-character chunk can cut a sentence or word in half (e.g. "Automatic do..." instead of "Automatic docs"). This is a real tradeoff — smaller chunks are more precise but lose context; larger chunks keep context but are less precise. Chunk size needs to be tuned based on content.

## Embeddings
An embedding converts text into a list of numbers (a vector) that represents its meaning. Similar meanings produce similar vectors, even if the exact words are different. The model `all-MiniLM-L6-v2` from `sentence-transformers` converts each chunk into a vector of 384 numbers.

## Cosine similarity
To find which chunk is most relevant to a question, the question itself is also converted into a 384-number embedding. Then cosine similarity is calculated between the question's vector and every chunk's vector. Cosine similarity measures the angle between two vectors — a score close to 1 means very similar meaning, close to 0 means unrelated. The chunks with the highest similarity scores are returned as the most relevant ones (`top_k`).

## Why this works without exact keyword matching
Traditional search (like Ctrl+F) only finds exact words. Embeddings capture meaning, so a question phrased differently from the original text can still find the right chunk, because the underlying meaning is similar even if the words are not identical.

## Key takeaway
RAG has two separate stages:
1. **Indexing stage** (done once): chunk documents, convert to embeddings, store them
2. **Retrieval stage** (done per question): convert the question to an embedding, compare against stored chunk embeddings, return the top matches

These matches are then passed to the LLM to generate the final answer — which is the next step, not yet connected to the LLM.