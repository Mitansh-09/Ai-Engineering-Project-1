# Day 16 — Completed the full eval (finally)

## Result
20/20 correct (100%) on my 20-question test set.

## Why I'm skeptical of this number, not just happy about it
This is a misleadingly easy eval:
1. I wrote the questions myself, directly from my own notes, so they
   closely match the source wording. A real user would never phrase
   questions this precisely — this is closer to open-book exact recall
   than a genuine test of understanding.
2. Retrieval scores were all reasonable (0.34–0.59), meaning the
   chunking/embedding setup handles clean, well-matched queries fine.
   It says nothing about how it handles vague, poorly-worded, or
   genuinely ambiguous real-world questions.
3. The free LLM router happened to behave well this run. Days 10-11
   showed the same pipeline can "I don't know" or hallucinate on
   near-identical questions depending on which underlying free model
   gets picked. A 100% score here doesn't mean the system is 100%
   reliable — it means today's draw of free models was good.

## What a harder, more honest eval would need
- Questions phrased differently from the source text (paraphrased,
  not copied)
- Questions with answers split across multiple chunks
- Questions with no answer in the notes at all, to re-test the
  "I don't know" behavior at scale (not just 1-2 manual checks)
- Running the eval multiple times to see how much free-model
  variance affects the score

## Key takeaway
A 100% score on an eval you wrote yourself is a floor, not a ceiling —
it confirms the basic pipeline works, not that it's production-ready.
The honest version of this result for a resume/interview is "100% on
an initial self-authored eval set" with the caveats above stated
openly, not just "100% accuracy."