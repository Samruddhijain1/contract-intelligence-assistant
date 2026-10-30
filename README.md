# Contract Intelligence Assistant

A small evidence-first legal passage retrieval demo. It uses TF-IDF to rank contract passages and displays the source file, character offsets, and text. It is a retrieval prototype, not legal advice.

## Setup
Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Dataset setup
Use the public `awinml/legalbench-rag` dataset mirror specified in the assignment. Download only `benchmarks/cuad.json` and `corpus/cuad/` into:
- `data/benchmarks/cuad.json`
- `data/corpus/cuad/`

The corpus directory should contain the CUAD text contract files. Keep the original contract text unchanged because the benchmark uses character offsets. This repository intentionally does not redistribute the dataset.

## Run
```bash
streamlit run app.py
python cli.py "Does this agreement allow sublicensing?"
python evaluate.py
python improve.py
pytest -q
```

## Architecture
1. `benchmark.py`: deterministic 194-query mini selection and required hash-based split.
2. `retrieval.py`: UTF-8 contract loading, overlapping character chunks, TF-IDF indexing and ranked search.
3. `app.py` / `cli.py`: web and terminal interfaces.
4. `evaluate.py`: first-pass document-level retrieval evaluation.
5. `improve.py`: baseline plus five recorded train-only configuration experiments.
6. `unanswerable_queries.json`: initial 30 labeled questions; do not edit after committing.

## Assumptions and Limitations

- The system uses TF-IDF-based lexical retrieval instead of an LLM to keep it simple, lightweight, and reproducible.
- Contract documents are divided into overlapping chunks to improve passage retrieval while preserving original character offsets.
- The relevance threshold is a heuristic, not a probability, and should be tuned using training data only.
- TF-IDF may miss paraphrases, semantic similarities, and complex legal cross-references.
- Character-level precision and recall are used to evaluate retrieval quality against annotated benchmark spans.
- The system retrieves contract evidence but does not provide legal advice or guarantee legal correctness.
- For production use, additional access controls, audit logs, stronger abstention, and legal review would be required.
