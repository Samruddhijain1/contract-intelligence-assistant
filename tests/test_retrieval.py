
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from retrieval import chunk_document, ContractRetriever


def test_chunk_document_preserves_offsets():
    doc = {
        "file_path": "sample.txt",
        "text": "A" * 2500
    }

    chunks = chunk_document(
        doc, chunk_chars=1200, overlap_chars=200
    )

    assert len(chunks) >= 2

    for chunk in chunks:
        assert chunk["text"] == doc["text"][
            chunk["start"]:chunk["end"]
        ]


def test_retriever_returns_ranked_results():
    chunks = [
        {
            "file_path": "a.txt",
            "text": "The licensee may sublicense the agreement.",
            "start": 0,
            "end": 43
        },
        {
            "file_path": "b.txt",
            "text": "Payment must be made within thirty days.",
            "start": 0,
            "end": 41
        }
    ]

    retriever = ContractRetriever(
        chunks,
        config={"ngram_max": 2, "min_df": 1, "top_k": 2,
                "min_score": 0.0}
    )

    results = retriever.search(
        "sublicense agreement", top_k=2, min_score=0.0
    )

    assert len(results) == 2
    assert results[0]["file_path"] == "a.txt"
    assert results[0]["score"] >= results[1]["score"]


def test_empty_query_returns_no_results():
    retriever = ContractRetriever([], config={})
    assert retriever.search("test") == []
