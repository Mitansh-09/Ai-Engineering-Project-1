# Day 12 — Conversation History (multi-turn agent)

## What changed
Added a `history` field to AgentState — a list of past
{role, content} messages. Both rag_node and general_node now:
1. Read existing history from state
2. Include it in the messages sent to the LLM (for general_node) or
   just track it (for rag_node, since RAG uses a single context-stuffed
   prompt rather than a chat history)
3. Append the new question + answer to history and return it, so it
   persists across multiple invoke() calls

## Why this matters
Without history, every question is treated in isolation — the agent
has no idea what "its" or "that" refers to if the user asks a follow-up.
Real chat interfaces need this to feel like an actual conversation
rather than a series of disconnected one-off questions.

## Test result
Q1: "What is the capital of France?" → "Paris"
Q2: "What is its population?" → correctly understood "its" = Paris,
gave both city-proper (~2.1M) and metro area (~12.5M) figures.

This confirms history was actually passed to the LLM and used — if it
hadn't been, "its population" would have been meaningless to the model
on its own.

## Limitation I noticed
rag_node's generate_answer() doesn't currently use history at all — it
only uses the current question for retrieval and generation. So a
follow-up like "tell me more about that" would fail to retrieve
anything useful if routed to rag_node, since the retrieval query
wouldn't have the context of what "that" refers to.

## Key takeaway
Adding history to general_node was simple (just include past messages
in the API call). Making RAG properly multi-turn is harder — the
retrieval step itself would need to account for conversation context
(e.g., rewriting the follow-up question using prior turns before
embedding it), which is a deeper fix than what I built today.