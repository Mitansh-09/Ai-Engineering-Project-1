# Day 11 — Conditional Routing + Real Model Reliability Issues

## What I built
A 3-node LangGraph agent:
- classify_node: decides if a question needs the notes knowledge base or general knowledge
- rag_node: runs the existing RAG pipeline (retrieve + generate)
- general_node: sends the question straight to the LLM, no retrieval
- route(): a function used with add_conditional_edges() to pick which node runs next based on classify_node's decision

This is the first graph with actual branching — the path isn't fixed,
it depends on a decision made mid-graph.

## Bug 1: classify_node routed incorrectly
First version of the classify prompt was too vague ("does this need
notes or general knowledge?"). A clearly notes-based question ("what
does tool calling let the model do") got routed to "general" — so
rag_node never even ran, and the model answered from its own training
instead of my notes. Fixed by making the prompt explicit about what
topics the notes actually cover, instead of leaving it to guess.

## Debugging approach
Added print statements in route() and rag_node() to see exactly which
path the graph took and what context it retrieved. This was the only
way to catch that rag_node wasn't running at all — the wrong answer
alone didn't make that obvious.

## Bug 2 (unresolved, documented as a real limitation): bad generation even with correct context
After fixing routing, retrieval correctly found the right chunks
(scores 0.634, 0.537, 0.503, all genuinely about tool calling). But
the LLM still produced a confused, half-quoted, incoherent answer —
it latched onto an unrelated chunk (about RAG sources, not tool
calling) and garbled a sentence from it instead of using the clearly
best-scored chunk properly.

## Three distinct failure modes observed across Day 10-11
1. Says "I don't know" even when the answer IS in the retrieved context
2. Ignores the context entirely, answers from its own general training
3. Uses the context but misreads/garbles it into an incoherent answer

All three point to the same root cause: openrouter/free serves a
different underlying free model on every call, and these models vary
wildly in how well they follow instructions like "use only this
context" or "pick the most relevant chunk."

## Key takeaway
This is exactly why production RAG systems don't rely on random free
models for anything user-facing — and exactly why Day 8's evals
matter. Without a systematic test set, these failures would be
invisible; you'd only notice them if you happened to ask the one
question that broke that run. A fixed, reliable model (or at minimum
re-running eval.py regularly against a consistent model) is necessary
before trusting this kind of agent in front of real users.