# Day 4 — RAG Part 2 (Generation)

## What changed from Day 3
Day 3 only did retrieval — finding the right chunks for a question.
Day 4 connects retrieval to the LLM, completing the full RAG pipeline.

## The full pipeline
1. User asks a question
2. Question is embedded (converted to a vector)
3. Cosine similarity finds the top-k most relevant chunks
4. Those chunks are combined into a "context" string
5. The context + question are sent to the LLM in one prompt
6. LLM generates an answer using only that context

## Provider switch
Used Anthropic's API first, but hit a credit balance error (free trial
exhausted). Switched to OpenRouter's "openrouter/free" router, which
automatically picks from available free models instead of a hardcoded
slug (hardcoded free model slugs go unavailable without notice).

## Why the prompt matters
The instruction "Answer using ONLY the context below. If the context
doesn't contain the answer, say 'I don't know'" is critical.

Tested this directly:
- Q: "What does the --reload flag do?" (answer IS in notes)
  → Correct answer, matched the notes exactly.
- Q: "What is Docker?" (answer is NOT in notes)
  → Model correctly said "I don't know" instead of making something up.
- Q: "What does tool calling let the model do?" (answer IS in notes)
  → Correct, detailed answer using only the retrieved context.

This confirms the instruction prevents hallucination — without it,
the model would likely answer Docker questions from its own general
knowledge, which defeats the point of RAG (answering from MY data).

## Chunk size experiment
Changed chunk_size from 500 to 300. Chunk count went from 11 to 19.
Retrieval scores shifted slightly (0.358 → 0.321 for the same query),
but final answers stayed correct. With only 2 small notes files as the
knowledge base, the effect was minor — a bigger effect would likely
show on a larger, more varied document set.

## Key takeaway
Retrieval decides WHAT information the LLM sees.
Generation decides HOW that information gets turned into an answer.
The "I don't know" test is the clearest way to verify RAG is actually
constraining the model to your data, not just decorating a normal
chatbot response.