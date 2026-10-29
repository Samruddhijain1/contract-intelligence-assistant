import argparse
from pathlib import Path
from retrieval import build_retriever

def main():
    parser = argparse.ArgumentParser(description="Search indexed legal contract passages.")
    parser.add_argument("question", help="Natural-language question")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--threshold", type=float, default=0.08)
    parser.add_argument("--corpus", default="data/corpus/cuad")
    args = parser.parse_args()
    try:
        engine = build_retriever(Path(args.corpus))
    except Exception as exc:
        raise SystemExit(f"Index error: {exc}")
    results = engine.search(args.question, args.top_k, args.threshold)
    if not results:
        print("ABSTAIN: No passage met the relevance threshold.")
        return
    for i, r in enumerate(results, 1):
        print(f"\n[{i}] score={r['score']:.3f} | {r['file_path']} | offsets [{r['start']}:{r['end']}]")
        print(r["text"][:1600])

if __name__ == "__main__":
    main()
