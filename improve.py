"""Small reproducible parameter sweep. Uses train split only; logs every trial."""
import json
from pathlib import Path
from benchmark import load_benchmark
from retrieval import build_retriever, load_config, ContractRetriever, read_contracts, chunk_document

def main():
    tests = [x for x in load_benchmark() if x["split"] == "train"]
    cfg = load_config()
    docs = read_contracts(Path("data/corpus/cuad"))
    log = []
    # Baseline + five explicit configurations (iterations 1-5).
    trials = [
        ("baseline", 1200, 200, 1, 0.08),
        ("iter1 smaller chunks", 800, 120, 1, 0.08),
        ("iter2 larger chunks", 1600, 250, 1, 0.08),
        ("iter3 unigram", 1200, 200, 1, 0.08),
        ("iter4 bigrams", 1200, 200, 2, 0.08),
        ("iter5 lower abstention threshold", 1200, 200, 2, 0.03),
    ]
    for name, size, overlap, ngram, threshold in trials:
        chunks = []
        for doc in docs:
            chunks.extend(chunk_document(doc, size, overlap))
        trial_cfg = dict(cfg, chunk_chars=size, overlap_chars=overlap, ngram_max=ngram)
        engine = ContractRetriever(chunks, trial_cfg)
        hits = 0
        for q in tests:
            results = engine.search(q["query"], top_k=5)
            retrieved = {Path(r["file_path"]).name.lower() for r in results}
            gold = {Path(s["file_path"]).name.lower() for s in q.get("snippets", [])}
            hits += bool(retrieved & gold)
        metric = hits / len(tests) if tests else 0.0
        log.append({"iteration": name, "train_queries": len(tests), "document_hit_rate_at_5": metric,
                    "chunk_chars": size, "overlap_chars": overlap, "ngram_max": ngram,
                    "threshold": threshold, "decision": "recorded; compare against baseline before selecting"})
    out = Path("data/results"); out.mkdir(parents=True, exist_ok=True)
    (out / "experiment_log.json").write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(json.dumps(log, indent=2))
    print("Review measured results; this simple sweep does not automatically claim an improvement.")

if __name__ == "__main__":
    main()
