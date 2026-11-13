# Project Summary — RAG API with Agentic Routing

## What this project does
I built an API that answers questions using my own study notes instead
of just the model's general knowledge. It retrieves the most relevant
notes for a question, gives them to an LLM as context, and the LLM
answers only from that context — saying "I don't know" if the answer
isn't there. On top of that, I added an agent layer that decides
whether a question even needs my notes, or if it's general knowledge
that doesn't need retrieval at all.

## Architecture (high level)
1. Notes are split into chunks and converted into embeddings
2. A question also gets converted into an embedding
3. Cosine similarity finds the most relevant chunks
4. Those chunks become context, sent to an LLM with a strict instruction
   to only answer from that context
5. A LangGraph agent sits on top: it first classifies whether a
   question needs the notes at all, then routes to either the RAG
   pipeline or a plain LLM call
6. The whole thing is wrapped in a FastAPI endpoint and deployed on Render

## Key technical decisions and why
- **Hand-written cosine similarity instead of a vector DB:** I wanted
  to actually understand what retrieval is doing under the hood before
  using a library that hides it. I'd switch to a real vector DB
  (Qdrant/FAISS) if this needed to scale past a few hundred chunks.
- **HuggingFace API for embeddings instead of a local model:** I
  originally ran sentence-transformers locally, but Render's free tier
  only gives 512MB RAM, and torch + transformers alone blew past that.
  Moving embeddings to an API call fixed it, and it's actually closer
  to how production systems work anyway.
- **OpenRouter's free router for the LLM:** it let me build and test
  everything without paying, but it comes with a real cost — it picks
  a different underlying free model every call, so answer quality is
  inconsistent. I documented this as a known limitation instead of
  hiding it.
- **LangGraph for the agent layer:** I wanted the system to make an
  actual decision (does this need retrieval or not) instead of always
  following the same fixed path. LangGraph's state/node/conditional-edge
  model made that straightforward to build.

## Bugs I hit and fixed (my top 3)
1. **Silent None bug:** get_embedding() was missing a return statement
   after I added debug prints and accidentally deleted it. The function
   kept "working" but returned None every time, which only showed up
   later as a confusing `None * float` error deep in the retrieval math.
   This taught me to check for a missing return first whenever
   something runs without crashing but produces None-related errors.
2. **Deployment ran out of memory:** sentence-transformers + torch
   needed more RAM than Render's free tier (512MB) allows. Traced it
   through several failed attempts (OpenRouter embeddings aren't free,
   a retired HuggingFace URL, a missing token permission) before
   landing on the HuggingFace Inference Router with the right scope.
3. **Agent routed to the wrong node:** my first classify_node prompt
   was too vague, so a clearly notes-based question got routed to
   "general" instead of "rag" — meaning retrieval never even ran. I
   only caught this by adding print statements to see which path the
   graph actually took, not just by looking at the wrong final answer.

## Known limitations
1. The free LLM router is inconsistent — the same question can get a
   correct answer, a hallucinated one, or a confused one depending on
   which underlying free model gets picked that call.
2. Conversation history is only used by the general-knowledge node —
   the RAG node doesn't yet use prior conversation turns, so a
   follow-up question like "tell me more about that" would fail to
   retrieve anything relevant if routed to RAG.
3. Retrieval quality was only evaluated on 1-3 manual questions and a
   partially-run 20-question eval set — never completed a full
   measured accuracy number due to hitting OpenRouter's daily rate limit.

## What I'd build next with more time
1. Finish the full eval run and get a real accuracy percentage, then
   use it to compare chunk sizes and retrieval strategies properly
   instead of just eyeballing a few examples.
2. Make retrieval history-aware, so follow-up questions in RAG mode
   actually retrieve the right thing.
3. Swap the free LLM router for a fixed, paid model to get consistent,
   reliable answers instead of three different failure modes depending
   on luck.
   
   ## Agent capabilities (added Day 10-14)
- Conditional routing: classifies each question as notes-based or
  general knowledge, routes accordingly via LangGraph
- Multi-turn conversation: tracks history across turns
- Query reformulation: rewrites ambiguous follow-ups into standalone
  questions using conversation history, before retrieval

## Additional bugs fixed
4. Agent routing ignored conversation context — classify_node only
   saw the current question, so follow-ups got misrouted. Fixed by
   passing history into the classification prompt too.