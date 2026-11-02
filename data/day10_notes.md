# Day 10 — First LangGraph Agent (single node)

## Core concepts (from video + code)
- **State**: a shared dictionary (TypedDict) that flows through the
  graph. Each node reads from it and returns updates to it.
- **Node**: a Python function that takes the state and returns a
  partial state update. In my code, answer_node() takes the question
  from state and returns {"answer": ...}.
- **Edge**: defines what runs after what. set_entry_point() says where
  the graph starts; add_edge("answer", END) says the graph finishes
  after that node.

## What I built
A minimal LangGraph with ONE node that just wraps my existing
generate_answer() function. This isn't really "agentic" yet — it's
the same RAG pipeline, just running inside LangGraph's structure
instead of being called directly. The real agent behavior (multiple
nodes, decisions, tool choice) comes next.

## Bug: forgot load_knowledge_base()
Got a None * float error identical to past bugs. Cause: agent.py never
called load_knowledge_base() before invoking the graph, so _embeddings
stayed None. Lesson reinforced: any new file using rag.engine's
retrieve()/generate_answer() must call load_knowledge_base() first —
this is now the first thing I check when I see a None-related crash.

## Interesting observation: inconsistent free model answers
Ran the exact same question twice. First run: "I don't know" (wrong —
the answer was clearly in the notes). Second run: a correct, detailed
answer. Cause: openrouter/free picks a different underlying free model
each call, and some follow the retrieved context better than others.
This is a real limitation of free-tier LLMs — production systems use
paid, consistent models for exactly this reason.

## Key takeaway
A LangGraph "agent" with one node and no branching is just a RAG
pipeline wrapped in extra structure. The value of LangGraph shows up
with multiple nodes and conditional routing — which is Day 11.