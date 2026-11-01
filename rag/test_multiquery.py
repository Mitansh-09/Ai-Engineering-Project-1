from rag.engine import load_knowledge_base, retrieve, retrieve_multi_query

load_knowledge_base(["data/day1_notes.md", "data/day2_notes.md"])

query = "reload flag purpose"

normal = retrieve(query)
print("--- Normal retrieval ---")
for r in normal:
    print(f"{r['score']:.3f} | {r['text'][:80]}")

multi = retrieve_multi_query(query)
print("\n--- Multi-query retrieval ---")
for r in multi:
    print(f"{r['score']:.3f} | {r['text'][:80]}")