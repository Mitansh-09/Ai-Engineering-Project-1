# Day 6 — Deployment:

## What happened
Tried deploying to Render, hit a chain of failures:
1. requirements.txt had unrelated global packages (not from a clean venv) —
   fixed by writing it manually with only actual dependencies.
2. OpenRouter doesn't offer free embeddings (only free chat models) — got
   a 402 credit error.
3. Tried sentence-transformers locally on Render — ran out of memory
   (512MB free tier can't hold torch + transformers + the model).
4. Switched to HuggingFace's embedding API instead of a local model —
   but the old api-inference.huggingface.co URL is retired.
5. Found the new URL: router.huggingface.co/hf-inference/models/{model}/pipeline/feature-extraction
6. Got a 403 — the HF token didn't have "Make calls to Inference Providers"
   permission. Had to generate a new fine-grained token with that scope
   explicitly checked.

## Key takeaway
Free tier hosting (512MB RAM) can't run local embedding models with torch —
that stack needs gigabytes. The fix was moving embeddings to an API call
instead of local inference. This is actually how production RAG systems
work too — you rarely run embedding models on your own API server.

## Second takeaway
"It works on my machine" isn't the same as "it works in production."
Deployment surfaced memory limits, retired APIs, and permission scopes
that never showed up in local testing.