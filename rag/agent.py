from langgraph.graph import StateGraph, END
from typing import TypedDict
from rag.engine import generate_answer, load_knowledge_base
import requests
import os

load_knowledge_base([
    "data/day1_notes.md", "data/day2_notes.md", "data/day3_notes.md",
    "data/day4_notes.md", "data/day5_notes.md", "data/day6_notes.md"
])

class AgentState(TypedDict):
    question: str
    answer: str
    needs_notes: bool

def classify_node(state: AgentState):
    prompt = f"""You have a knowledge base of personal study notes covering: FastAPI, LLM APIs, tool calling, agents, RAG (chunking/embeddings/retrieval), and deployment.

Does this question relate to any of those specific topics (answer "notes"), or is it unrelated general knowledge like geography, history, etc. (answer "general")?

Reply with ONLY one word: "notes" or "general".

Question: {state['question']}"""

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"},
        json={"model": "openrouter/free", "messages": [{"role": "user", "content": prompt}]}
    )
    data = response.json()
    decision = data.get("choices", [{}])[0].get("message", {}).get("content", "notes").strip().lower()
    return {"needs_notes": "notes" in decision}

def rag_node(state: AgentState):
    result = generate_answer(state["question"])
    print("\n=== RETRIEVED CONTEXT (what the model SHOULD have used) ===")
    for s in result["sources"]:
        print(f"score={s['score']:.3f} | {s['text'][:200]}")
    print("=== END CONTEXT ===\n")
    return {"answer": result["answer"]}

def general_node(state: AgentState):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"},
        json={"model": "openrouter/free", "messages": [{"role": "user", "content": state["question"]}]}
    )
    data = response.json()
    answer = data.get("choices", [{}])[0].get("message", {}).get("content", "ERROR")
    return {"answer": answer}

def route(state: AgentState):
    decision = "rag" if state["needs_notes"] else "general"
    print(f"\n>>> ROUTING DECISION: {decision} <<<\n")
    return decision

graph = StateGraph(AgentState)
graph.add_node("classify", classify_node)
graph.add_node("rag", rag_node)
graph.add_node("general", general_node)

graph.set_entry_point("classify")
graph.add_conditional_edges("classify", route, {"rag": "rag", "general": "general"})
graph.add_edge("rag", END)
graph.add_edge("general", END)

app = graph.compile()

if __name__ == "__main__":
    q1 = app.invoke({"question": "What does tool calling let the model do?"})
    print("Q1 (should use notes):", q1["answer"])

    q2 = app.invoke({"question": "What is the capital of France?"})
    print("\nQ2 (should use general knowledge):", q2["answer"])