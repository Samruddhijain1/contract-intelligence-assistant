"""Load the assignment's deterministic 194-query CUAD mini benchmark."""
import hashlib, json, random
from pathlib import Path

def mini(tests, n=194):
    if len(tests) <= n:
        return tests
    def key(t):
        random.seed(t["snippets"][0]["file_path"])
        return random.random()
    return sorted(tests, key=key)[:n]

def assign_split(query: str) -> str:
    h = int(hashlib.sha256(query.strip().encode("utf-8")).hexdigest(), 16)
    return "test" if h % 10 < 3 else "train"

def load_benchmark(path="data/benchmarks/cuad.json"):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    tests = mini(data["tests"])
    for item in tests:
        item["split"] = assign_split(item["query"])
    return tests
