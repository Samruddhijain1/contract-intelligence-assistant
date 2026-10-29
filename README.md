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

## Assumptions and limitations
- This starter uses TF-IDF lexical retrieval, not an LLM. It is inexpensive and reproducible, but may miss paraphrases and cross-references.
- A relevance threshold is a heuristic, not a calibrated probability. The default should be tuned on train only.
- The evaluation starter reports document hit rate. The assignment requires character-level precision and recall; these must be implemented and validated against the benchmark's actual offset field names before claiming full compliance.
- The starter's retrieval offsets are passage offsets in the original file. Confirm that the benchmark's annotated answer text matches `document[start:end]` before trusting evaluation.
- For a production legal workflow, add access controls, audit logs, stronger abstention calibration, and legal review.

## AI tool usage
Disclose the actual tools used to assist development and describe which portions they helped with. Do not claim independent work for generated code. Be prepared to explain and modify every component.
