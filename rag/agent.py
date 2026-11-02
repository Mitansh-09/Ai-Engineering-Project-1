from langgraph.graph import StateGraph, END
from typing import TypedDict
from rag.engine import retrieve, generate_answer, load_knowledge_base

load_knowledge_base([
    "data/day1_notes.md",
    "data/day2_notes.md",
    "data/day3_notes.md",
    "data/day4_notes.md",
    "data/day5_notes.md",
    "data/day6_notes.md"
])

class AgentState(TypedDict):
    question: str
    answer: str

def answer_node(state: AgentState):
    result = generate_answer(state["question"])
    return {"answer": result["answer"]}

graph = StateGraph(AgentState)
graph.add_node("answer", answer_node)
graph.set_entry_point("answer")
graph.add_edge("answer", END)

app = graph.compile()

if __name__ == "__main__":
    result = app.invoke({"question": "What does tool calling let the model do?"})
    print(result["answer"])