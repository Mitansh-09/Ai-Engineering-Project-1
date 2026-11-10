# Day 14 — Query Reformulation (closing Day 12's gap)

## What changed
Added reformulate_query() in rag/engine.py: given a follow-up question
and recent conversation history, it asks the LLM to rewrite the
question as a standalone version with all context included. rag_node
now calls this before retrieval, so ambiguous follow-ups (e.g. "give
me an example of that") get resolved into a clear, self-contained
query before being embedded and searched.

## Bug found while testing this fix
First test attempt showed the follow-up routed to "general" instead of
"rag" — meaning reformulate_query() never ran at all. Root cause:
classify_node only looked at the current question in isolation, with
no conversation history, so "give me an example of that" looked like
generic small talk rather than a notes-related follow-up. Fixed by
passing history into classify_node's prompt too, not just rag_node's.

## Test result after fix
- Q1: "What does tool calling let the model do?" (no history) →
  routed to rag correctly, reformulation left it unchanged (expected,
  since there's nothing to resolve yet)
- Q2: "Give me an example of that" (with history) → routed to rag
  correctly, reformulated to "Can you give me an example of what tool
  calling lets a model do?" — the ambiguous "that" was correctly
  resolved using conversation history
- Q1's actual answer was wrong this run ("I don't know" despite the
  answer being in context) — but this is the known free-model
  inconsistency issue from Day 10-11, not a reformulation bug. The
  reformulation step itself worked exactly as intended.

## Key takeaway
A fix often needs more than the one function you planned to change.
I only intended to touch rag_node's retrieval step, but the real
blocker was classify_node's routing decision having no awareness of
conversation context at all. Testing end-to-end (not just the new
function in isolation) is what surfaced that.