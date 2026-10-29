
import json
import hashlib
from pathlib import Path

def assign_split(query):
    h = int(
        hashlib.sha256(query.strip().encode("utf-8")).hexdigest(),
        16
    )
    return "test" if h % 10 < 3 else "train"

questions = json.loads(
    Path("unanswerable_queries.json").read_text(encoding="utf-8")
)

train = sum(assign_split(q["query"]) == "train" for q in questions)
test = sum(assign_split(q["query"]) == "test" for q in questions)

print("Total:", len(questions))
print("Train:", train)
print("Test:", test)

Path("data/results").mkdir(parents=True, exist_ok=True)
Path("data/results/unanswerable_split_counts.json").write_text(
    json.dumps({
        "total": len(questions),
        "train": train,
        "test": test
    }, indent=2),
    encoding="utf-8"
)
print("Counts saved.")
