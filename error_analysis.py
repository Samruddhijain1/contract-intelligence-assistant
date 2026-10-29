
import json
from pathlib import Path
from benchmark import load_benchmark
from retrieval import build_retriever

engine = build_retriever(Path("data/corpus/cuad"))
questions = [q for q in load_benchmark() if q["split"] == "train"]

failures = []

for q in questions:
    gold = [
        (s["file_path"].replace("\\", "/").lower(), *map(int, s["span"]))
        for s in q.get("snippets", [])
    ]

    results = engine.search(q["query"], top_k=5, min_score=0.0)

    overlap = 0
    for r in results:
        rp = r["file_path"].replace("\\", "/").lower()
        for gp, gs, ge in gold:
            if rp.endswith(gp) or gp.endswith(rp):
                overlap += max(0, min(r["end"], ge) - max(r["start"], gs))

    if overlap == 0:
        cause = "Wrong document or no gold-span overlap"
    else:
        cause = "Partial answer-span coverage; inspect manually"

    failures.append({
        "query": q["query"],
        "diagnosed_cause": cause,
        "gold_spans": [
            {"file": p, "start": s, "end": e} for p, s, e in gold
        ],
        "retrieved": [
            {
                "file": Path(r["file_path"]).name,
                "start": r["start"],
                "end": r["end"],
                "score": round(r["score"], 4),
                "text": r["text"][:350]
            }
            for r in results
        ],
        "overlap_characters": overlap
    })

# Zero-overlap cases first, then lowest-overlap cases.
failures.sort(key=lambda x: x["overlap_characters"])
selected = failures[:10]

out = Path("data/results")
out.mkdir(parents=True, exist_ok=True)
(out / "error_analysis.json").write_text(
    json.dumps(selected, indent=2), encoding="utf-8"
)

print("Training queries examined:", len(questions))
print("Failure examples saved:", len(selected))
print("Output: data/results/error_analysis.json")
for i, item in enumerate(selected, 1):
    print(f"{i}. {item['query']}")
    print("   Cause:", item["diagnosed_cause"])
    print("   Overlap characters:", item["overlap_characters"])

