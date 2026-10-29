
import json
import hashlib
from pathlib import Path

from benchmark import load_benchmark
from retrieval import build_retriever

CORPUS = Path("data/corpus")
RESULTS = Path("data/results")


def split_query(query):
    h = int(
        hashlib.sha256(query.strip().encode("utf-8")).hexdigest(),
        16
    )
    return "test" if h % 10 < 3 else "train"


def doc_key(path):
    """Match benchmark paths like cuad/file.txt to corpus paths."""
    p = str(path).replace("\\", "/").lower()
    marker = "/cuad/"
    if marker in p:
        return p.split(marker, 1)[1]
    return p.removeprefix("cuad/").removeprefix("./")


def merge(intervals):
    merged = []
    for start, end in sorted(intervals):
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return merged


def character_metrics(retrieved, gold):
    # Group character ranges by canonical document path.
    rdocs, gdocs = {}, {}

    for path, start, end in retrieved:
        rdocs.setdefault(doc_key(path), []).append((start, end))

    for path, start, end in gold:
        gdocs.setdefault(doc_key(path), []).append((start, end))

    rdocs = {p: merge(v) for p, v in rdocs.items()}
    gdocs = {p: merge(v) for p, v in gdocs.items()}

    retrieved_chars = sum(
        end - start for ranges in rdocs.values()
        for start, end in ranges
    )
    gold_chars = sum(
        end - start for ranges in gdocs.values()
        for start, end in ranges
    )

    overlap = 0
    for path, rranges in rdocs.items():
        for rs, re in rranges:
            for gs, ge in gdocs.get(path, []):
                overlap += max(0, min(re, ge) - max(rs, gs))

    precision = overlap / retrieved_chars if retrieved_chars else 0.0
    recall = overlap / gold_chars if gold_chars else 0.0
    return precision, recall


def gold_spans(item):
    spans = []
    for snippet in item.get("snippets", []):
        path = snippet["file_path"]
        start, end = map(int, snippet["span"])
        spans.append((path, start, end))
    return spans


def main():
    engine = build_retriever(CORPUS / "cuad")
    benchmark = load_benchmark()
    rows = []

    # Answerable benchmark evaluation.
    for split in ("train", "test"):
        subset = [q for q in benchmark if q["split"] == split]

        for k in (1, 3, 5):
            precisions, recalls = [], []
            no_results = 0

            for item in subset:
                results = engine.search(item["query"], top_k=k)
                if not results:
                    no_results += 1

                retrieved = [
                    (r["file_path"], r["start"], r["end"])
                    for r in results
                ]

                p, r = character_metrics(
                    retrieved, gold_spans(item)
                )
                precisions.append(p)
                recalls.append(r)

            rows.append({
                "type": "answerable",
                "split": split,
                "k": k,
                "queries": len(subset),
                "mean_character_precision": (
                    sum(precisions) / len(precisions)
                    if precisions else 0.0
                ),
                "mean_character_recall": (
                    sum(recalls) / len(recalls)
                    if recalls else 0.0
                ),
                "no_result_count": no_results
            })

    # Unanswerable evaluation: count abstentions vs returned passages.
    unanswerable_path = Path("unanswerable_queries.json")
    if unanswerable_path.exists():
        questions = json.loads(
            unanswerable_path.read_text(encoding="utf-8")
        )

        for split in ("train", "test"):
            subset = [
                q for q in questions
                if split_query(q["query"]) == split
            ]

            abstained = sum(
                not engine.search(q["query"])
                for q in subset
            )

            rows.append({
                "type": "unanswerable",
                "split": split,
                "queries": len(subset),
                "correct_abstentions": abstained,
                "returned_results": len(subset) - abstained,
                "abstention_rate": (
                    abstained / len(subset) if subset else 0.0
                )
            })

    RESULTS.mkdir(parents=True, exist_ok=True)
    output = RESULTS / "span_evaluation.json"
    output.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    print(json.dumps(rows, indent=2))
    print(f"\nSaved measured results to {output}")


if __name__ == "__main__":
    main()
