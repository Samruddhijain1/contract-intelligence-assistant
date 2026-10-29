
import json
from pathlib import Path
from benchmark import mini

CORPUS = Path("data/corpus")

data = json.loads(
    Path("data/benchmarks/cuad.json").read_text(encoding="utf-8")
)
tests = mini(data["tests"])

def find_contract(file_path):
    target = str(file_path).replace("\\", "/").lower().lstrip("./")

    for path in CORPUS.rglob("*"):
        if not path.is_file():
            continue

        actual = str(path).replace("\\", "/").lower()
        if actual.endswith("/" + target) or actual == target:
            return path

    return None

checked = 0
matched = 0
missing_files = 0
examples = []

for test in tests:
    for snippet in test.get("snippets", []):
        file_path = snippet.get("file_path")
        span = snippet.get("span")
        answer = snippet.get("answer")

        if not file_path or not isinstance(span, list) or len(span) != 2:
            examples.append({
                "problem": "Unexpected snippet fields",
                "snippet": snippet
            })
            continue

        path = find_contract(file_path)

        if path is None:
            missing_files += 1
            if len(examples) < 5:
                examples.append({
                    "problem": "Contract file not found",
                    "file_path": file_path
                })
            continue

        document = path.read_text(encoding="utf-8")
        start, end = map(int, span)
        actual_answer = document[start:end]
        checked += 1

        if actual_answer == answer:
            matched += 1
        elif len(examples) < 5:
            examples.append({
                "problem": "Answer does not match span",
                "file": str(path),
                "span": span,
                "expected": str(answer)[:150],
                "actual": actual_answer[:150]
            })

print("Benchmark queries:", len(tests))
print("Spans checked:", checked)
print("Exact matches:", matched)
print("Mismatches:", checked - matched)
print("Missing contract files:", missing_files)
print(
    "Exact match rate:",
    round(matched / checked, 4) if checked else "N/A"
)

if examples:
    print("\nExamples requiring inspection:")
    for example in examples[:5]:
        print(json.dumps(example, indent=2))
