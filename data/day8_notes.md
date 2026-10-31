# Day 8 — Evals (measuring RAG quality systematically)

## What changed from manual testing
Until now, retrieval was tested by asking 3-4 questions manually and
eyeballing the answers. Today I built a proper test set — 20 questions
with known expected answers, pulled from my own Day 1-6 notes — and a
script to run all of them automatically and save the results.

## Eval script structure
- data/eval_questions.json: 20 {question, expected_answer} pairs
- rag/eval.py: loads the full knowledge base (all 6 notes files),
  runs generate_answer() on every question, saves results to
  data/eval_results.json, prints a comparison of expected vs actual

## Module import issue
Running `python3 rag/eval.py` failed with `ModuleNotFoundError: No
module named 'rag'`, even though eval.py is inside the rag/ folder and
pwd was correct. Fix: run it as a module instead of a script —
`python3 -m rag.eval` — so Python resolves the `rag` package import
correctly.

## Bug: missing return statement
Mid-run, retrieve() crashed with `TypeError: unsupported operand
type(s) for *: 'NoneType' and 'NoneType'`. Root cause: get_embedding()
had no `return` statement (it got deleted while editing in debug
prints earlier), so every embedding call silently returned None
instead of a vector. A function with no return always returns None in
Python — this is the first thing to check when something "runs" but
produces None-related errors.

## Hit OpenRouter's daily free-tier rate limit
After 1 successful question, question 2 failed with a 429 error:
"Rate limit exceeded: free-models-per-day" — the free tier allows 50
requests/day, and this project's testing over the past week used them
up. Options: wait for the daily reset, or add $10 credit to raise the
limit to 1000/day.

## Added error handling
The eval script originally crashed entirely on the first API failure,
losing all progress on the remaining questions. Fixed generate_answer()
to check for a missing "choices" key in the response and return an
"ERROR: ..." string instead of crashing, so one failed request doesn't
kill the whole batch — the rest of the questions still get processed
and graded.

## Key takeaway
A test suite is only useful if it survives individual failures. Hard
crashes on the first error (rate limits, timeouts, bad responses) waste
all the work already done. Real eval pipelines need to isolate
failures per test case, not let one bad request take down the whole run.

## Still pending
Full 20-question eval run + manual grading + accuracy % — blocked on
the OpenRouter daily rate limit resetting.