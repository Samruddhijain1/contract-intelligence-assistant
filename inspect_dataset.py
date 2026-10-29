
import json
from pathlib import Path

path = Path("data/benchmarks/cuad.json")
data = json.loads(path.read_text(encoding="utf-8"))

tests = data["tests"]
print("Total benchmark queries:", len(tests))

# Use the assignment's deterministic mini selection
import random

def mini(tests, n=194):
    if len(tests) <= n:
        return tests

    def key(t):
        random.seed(t["snippets"][0]["file_path"])
        return random.random()

    return sorted(tests, key=key)[:n]

tests = mini(tests)

print("\nFirst query fields:")
print(tests[0].keys())
print("\nFirst query:")
print(json.dumps(tests[0], indent=2)[:5000])

print("\nFirst snippet fields:")
print(tests[0]["snippets"][0].keys())
print("\nFirst snippet:")
print(json.dumps(tests[0]["snippets"][0], indent=2))
