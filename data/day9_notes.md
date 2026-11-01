# Day 9 — Multi-Query Retrieval

## What it does
Instead of embedding only the user's exact question, rewrite_query()
asks the LLM to generate 3 alternative phrasings of the same question.
retrieve_multi_query() then runs retrieval for all 4 versions (original
+ 3 rewrites), merges the results, deduplicates by text, and keeps the
highest score per chunk.

## Why this helps
A user's exact wording might not closely match the document's wording,
even if they mean the same thing. Generating alternate phrasings
increases the chance that at least one version closely matches how the
information is written in the source documents.

## Test result (query: "reload flag purpose")
- Normal retrieval top scores: 0.318, 0.301, 0.172
- Multi-query top scores: 0.333, 0.301, 0.195
- Top result was the same chunk in both cases, but multi-query scored
  it slightly higher and replaced a weaker 3rd-place match with a
  somewhat more relevant one.

## Honest limitation observed
On this small dataset (11 chunks), the improvement was minor — the top
result didn't change. Multi-query costs 3 extra LLM calls per question
(for rewriting), so on a small, low-ambiguity knowledge base it may not
be worth the extra latency and cost. It likely matters more on larger,
more varied document sets or with genuinely ambiguous queries.

## Key takeaway
Not every "advanced RAG" technique is worth the overhead for every
use case. Multi-query adds cost and latency for retrieval quality that
may barely improve on a small, well-structured dataset — this is a
real trade-off to mention in interviews, not just "I implemented it."