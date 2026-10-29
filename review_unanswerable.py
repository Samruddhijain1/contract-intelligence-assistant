
import json
from pathlib import Path
from retrieval import build_retriever

engine = build_retriever(Path("data/corpus/cuad"))
questions = json.loads(
    Path("unanswerable_queries.json").read_text(encoding="utf-8")
)

review = []

for q in questions:
    results = engine.search(q["query"], top_k=3)
    review.append({
        "id": q["id"],
        "query": q["query"],
        "retrieval_status": "ABSTAINED" if not results else "REVIEW REQUIRED",
        "manual_judgment": "pending",
        "results": [
            {
                "file": Path(r["file_path"]).name,
                "score": round(r["score"], 4),
                "text": r["text"][:500]
            }
            for r in results
        ]
    })

out = Path("data/results")
out.mkdir(parents=True, exist_ok=True)
(out / "unanswerable_review.json").write_text(
    json.dumps(review, indent=2), encoding="utf-8"
)

print("Review file created: data/results/unanswerable_review.json")
print("Queries requiring passage review:", sum(bool(x["results"]) for x in review))
print("Open the file and set manual_judgment to 'answerable' or 'unanswerable' after inspecting each result.")
