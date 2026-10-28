from fastapi import FastAPI
from rag.engine import load_knowledge_base, generate_answer

app = FastAPI()

@app.on_event("startup")
def startup():
    count = load_knowledge_base(["data/day1_notes.md", "data/day2_notes.md"])
    print(f"Loaded {count} chunks into knowledge base")

@app.get("/")
def home():
    return {"status": "alive"}

@app.post("/ask")
def ask(query: str):
    return generate_answer(query)