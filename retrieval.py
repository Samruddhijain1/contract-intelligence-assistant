"""Simple, explainable TF-IDF contract passage retrieval."""
import json
import re
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).parent
CONFIG_PATH = ROOT / "config.json"

def load_config():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

def read_contracts(corpus_dir):
    """Read UTF-8 text files recursively. Keep the exact text for offsets."""
    docs = []
    for path in sorted(Path(corpus_dir).rglob("*")):
        if path.is_file() and path.suffix.lower() in {".txt", ".text"}:
            try:
                text = path.read_text(encoding="utf-8")
                if text.strip():
                    docs.append({"file_path": str(path), "text": text})
            except (UnicodeDecodeError, OSError):
                continue
    return docs

def chunk_document(doc, chunk_chars=1200, overlap_chars=200):
    text = doc["text"]
    chunks, start = [], 0
    while start < len(text):
        end = min(len(text), start + chunk_chars)
        # Prefer a paragraph/sentence boundary near the end, but preserve offsets.
        if end < len(text):
            boundary = text.rfind("\n", start + chunk_chars // 2, end)
            if boundary > start:
                end = boundary
        passage = text[start:end]
        if passage.strip():
            chunks.append({
                "file_path": doc["file_path"],
                "text": passage,
                "start": start,
                "end": end
            })
        if end >= len(text):
            break
        start = max(start + 1, end - overlap_chars)
    return chunks

class ContractRetriever:
    def __init__(self, chunks, config=None):
        self.config = config or load_config()
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(
            lowercase=True, stop_words="english",
            ngram_range=(1, int(self.config.get("ngram_max", 2))),
            min_df=int(self.config.get("min_df", 1)),
            sublinear_tf=True
        )
        self.matrix = self.vectorizer.fit_transform([c["text"] for c in chunks]) if chunks else None

    def search(self, query, top_k=None, min_score=None):
        if not self.chunks or self.matrix is None or not query.strip():
            return []
        from sklearn.preprocessing import normalize

        query_vector = self.vectorizer.transform([query])
        scores = (query_vector @ self.matrix.T).toarray().ravel()
        top_k = int(top_k or self.config.get("top_k", 5))
        min_score = float(self.config.get("min_score", 0.08) if min_score is None else min_score)
        ranked = scores.argsort()[::-1]
        results = []
        for idx in ranked[:top_k]:
            score = float(scores[idx])
            if score < min_score:
                continue
            item = dict(self.chunks[int(idx)])
            item["score"] = score
            results.append(item)
        return results

def build_retriever(corpus_dir, config=None):
    cfg = config or load_config()
    docs = read_contracts(corpus_dir)
    chunks = []
    for doc in docs:
        chunks.extend(chunk_document(doc, int(cfg["chunk_chars"]), int(cfg["overlap_chars"])))
    if not chunks:
        raise RuntimeError(f"No text contracts found under {corpus_dir}. Check dataset paths/file extensions.")
    return ContractRetriever(chunks, cfg)
