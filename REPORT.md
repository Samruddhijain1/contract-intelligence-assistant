# Contract Intelligence Assistant — Evaluation Report

## 1. Summary

Built a TF-IDF-based legal contract passage retrieval system with a Streamlit web application and a command-line interface (CLI). The system ranks passages based on query similarity and returns source documents, character offsets, and passage text.

The system was evaluated on 194 answerable CUAD benchmark queries, comprising 140 training queries and 54 test queries, along with 30 manually created unanswerable queries. At k = 5, mean character-level recall was 6.56% on train and 12.00% on test. The system abstained on 1 of 22 unanswerable training queries and 0 of 8 unanswerable test queries, indicating that abstention needs significant improvement.

## 2. System Design

- **Chunking:** Overlapping character-based passages, configured through `config.json`.
- **Retrieval:** TF-IDF unigram/bigram features with cosine similarity.
- **Ranking:** Passages are ranked by their cosine similarity to the user's query.
- **Abstention:** A configurable minimum relevance score determines whether passages are returned.
- **Interfaces:** Streamlit web application and CLI.
- **Alternatives considered:** BM25, embedding-based retrieval, and LLM reranking were not implemented in this baseline due to the time constraint.

## 3. LLM Use

No LLM is used in the retrieval pipeline. This avoids API costs and prevents contract text from being sent to an external language model. The system uses lexical similarity, which is simple and reproducible but may struggle with paraphrased legal language.

## 4. Evaluation Setup

- **Benchmark:** LegalBench-RAG-mini, CUAD subset.
- **Answerable queries:** 194 total; 140 train and 54 test.
- **Unanswerable queries:** 30 manually created queries; 22 train and 8 test.
- **Split method:** Assignment-provided SHA-256 hash-based split.
- **Span validation:** 272 answer spans checked against the original UTF-8 contract text; 272 exact matches, zero mismatches, and zero missing contract files.
- **Retrieval metrics:** Mean character-level precision and recall at k = 1, 3, and 5.
- **Abstention metrics:** Number of unanswerable queries for which the system returns no passages versus one or more passages.
- **Evaluation integrity:** The test split is reserved for final reporting and should not be used to tune the retrieval configuration.
- **Test runs:** One evaluation output is available for this report. Record the actual number of test evaluations performed if additional runs were conducted.

## 5. Results

### 5.1 Answerable-query retrieval results

Character-level precision and recall were measured using the validated CUAD answer spans.

| Configuration | Split | k | Queries | Mean character precision | Mean character recall |
|---|---|---:|---:|---:|---:|
| TF-IDF baseline | Train | 1 | 140 | 0.000704 | 0.001176 |
| TF-IDF baseline | Train | 3 | 140 | 0.006930 | 0.041722 |
| TF-IDF baseline | Train | 5 | 140 | 0.008443 | 0.065616 |
| TF-IDF baseline | Test | 1 | 54 | 0.003186 | 0.018519 |
| TF-IDF baseline | Test | 3 | 54 | 0.006544 | 0.066231 |
| TF-IDF baseline | Test | 5 | 54 | 0.006355 | 0.120018 |

### 5.2 Parameter experiment results

Six configurations were evaluated on 140 training queries using document hit rate at k = 5.

| Configuration | Chunk size | Overlap | N-gram max | Threshold | Document hit rate @5 |
|---|---:|---:|---:|---:|---:|
| Baseline | 1200 | 200 | 1 | 0.08 | 0.9929 |
| Smaller chunks | 800 | 120 | 1 | 0.08 | 1.0000 |
| Larger chunks | 1600 | 250 | 1 | 0.08 | 0.9929 |
| Unigram configuration | 1200 | 200 | 1 | 0.08 | 0.9929 |
| Bigrams | 1200 | 200 | 2 | 0.08 | 1.0000 |
| Lower threshold | 1200 | 200 | 2 | 0.03 | 1.0000 |

The smaller-chunk configuration, bigram configuration, and lower-threshold configuration achieved a document hit rate of 1.0000 on the training set. This is an increase from the baseline of 0.9929, or approximately 0.71 percentage points.

The experiments do not establish which configuration generalizes best. The lower-threshold configuration also changes the abstention behavior, which requires separate evaluation. The final configuration should be selected using training-set character-level recall and precision, together with abstention guardrails, before a final test-set evaluation.

### 5.3 Unanswerable-query results

| Split | Queries | Correct abstentions | Returned results | Abstention rate |
|---|---:|---:|---:|---:|
| Train | 22 | 1 | 21 | 4.55% |
| Test | 8 | 0 | 8 | 0.00% |
| Total | 30 | 1 | 29 | 3.33% |

These values measure whether the retriever returned no passages. Returned passages have not all been manually assessed for whether they actually answer the query. Therefore, the results should not be interpreted as a fully validated false-acceptance rate.

## 6. Iteration History

The baseline TF-IDF configuration used 1200-character chunks, 200-character overlap, unigram features, and a minimum relevance threshold of 0.08.

Five alternative configurations were evaluated against the baseline on 140 training queries. Smaller chunks (800 characters with 120-character overlap) increased document hit rate at k = 5 from 0.9929 to 1.0000. Enabling bigram features also achieved 1.0000. Lowering the threshold to 0.03 while using bigram features retained the same training document hit rate.

The larger-chunk configuration and unigram configuration achieved 0.9929, matching the baseline. No configuration was automatically selected as the final system because the experiment script records measurements without implementing a complete acceptance/rejection policy.

The observed improvements are limited to document hit rate on training data. Further evaluation using character-level precision and recall, abstention performance, and held-out test data is required before claiming that any configuration is superior overall.

The baseline achieved a training document hit rate at k = 5 of 0.9929. Three configurations reached 1.0000: smaller chunks, bigram features, and bigram features with a lower relevance threshold. The acceptance rule selects configurations using training document hit rate only. These results do not establish improvements in character-level retrieval or abstention, which require separate evaluation.

## 7. Error Analysis

The evaluation results indicate that only a small proportion of annotated answer characters are covered by retrieved passages. At k = 5, mean character recall is 6.56% on train and 12.00% on test.

Potential failure categories to investigate include:

1. Wrong document retrieved.
2. Correct document but wrong section.
3. Partial answer-span coverage.
4. Legal terminology or paraphrase mismatch.
5. Cross-reference or definition dependencies.
6. Incorrect abstention or insufficiently selective retrieval.

At least 10 concrete failed queries must be extracted from actual retrieval outputs and reviewed before completing this section. Each should include the query, retrieved passage, gold span, diagnosed failure cause, and proposed correction. The aggregate metrics alone do not identify these individual failures.

## 8. Limitations and Next Steps

The current implementation uses lexical TF-IDF retrieval and overlapping character-based chunks. Its low character-level recall indicates that the retrieved passages often cover only a small portion of the annotated answer spans.

The abstention mechanism also requires improvement: it abstained on only 1 of 30 unanswerable queries. Returning no passages is a useful signal, but a returned passage must be inspected before determining whether the system answered an unanswerable question incorrectly.

Recommended next steps:

1. Investigate incorrect document and partial-span retrieval failures.
2. Compare TF-IDF with BM25 and hybrid retrieval.
3. Tune chunk size, overlap, and relevance thresholds using training data only.
4. Evaluate abstention with manually reviewed relevance labels.
5. Complete the automated improvement loop with failure diagnosis and acceptance/rejection criteria.
6. Validate the final system with legal-domain reviewers before any real-world use.
