import json
import time
from rag.engine import load_knowledge_base, generate_answer

load_knowledge_base([
    "data/day1_notes.md",
    "data/day2_notes.md",
    "data/day3_notes.md",
    "data/day4_notes.md",
    "data/day5_notes.md",
    "data/day6_notes.md"
])

with open("data/eval_questions.json") as f:
    questions = json.load(f)

results = []
for i, item in enumerate(questions):
    print(f"\nProcessing {i+1}/{len(questions)}...")
    result = generate_answer(item["question"])
    results.append({
        "question": item["question"],
        "expected": item["expected_answer"],
        "actual": result["answer"],
        "top_score": result["sources"][0]["score"]
    })
    time.sleep(2)  # avoid rate limiting

for r in results:
    print(f"\nQ: {r['question']}")
    print(f"Expected: {r['expected']}")
    print(f"Got: {r['actual']}")
    print(f"Top retrieval score: {r['top_score']:.3f}")

with open("data/eval_results.json", "w") as f:
    json.dump(results, f, indent=2)