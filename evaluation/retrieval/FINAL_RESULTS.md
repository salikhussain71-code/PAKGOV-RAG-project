# PAKGOV-RAG - Final Retrieval Results - 100% Verified

## Dataset
- Chunks: 6711
- QA: 50 verified (15 en, 15 ur, 20 mixed)
- Model: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 384 dim
- Urdu-English similarity: 0.8370

## Retrieval Comparison - Same 50 QA - Fair

| Retriever | R@1 | R@3 | R@5 | R@10 | MRR |
|---|---|---|---|---|---|
| BM25 | 0.360 | 0.580 | 0.640 | 0.680 | 0.469 |
| Dense Multilingual | 0.440 | 0.600 | 0.620 | 0.740 | 0.535 |
| Hybrid RRF k=60 | 0.500 | 0.660 | 0.740 | 0.820 | 0.605 |

## Key Findings - No sugarcoating
- BM25 R@5 0.640 > Dense R@5 0.620 but Dense MRR 0.535 > BM25 0.469 - Dense ranks better
- RRF Hybrid R@5 0.740 beats both by +10% - R@10 0.820
- Failure at R@5: 13/50 (26%) - categorized in failure_analysis_50.md
- Grounded generation: 37 cited (74.0%) + 13 insufficient (26.0%) - matches R@5

## Urdu Support Stage 138
- Unicode NFC normalized: OK
- Embedding shape: [5, 384] - Official 384
- Urdu-English semantic similarity: 0.8370 >0.5 threshold
- QA lang distribution: mixed 20, ur 15, en 15

## Files - Raw Evidence - Not Typed Memory
- data/interim/bm25_results_50.jsonl
- data/interim/dense_results_50.jsonl
- data/interim/hybrid_rrf_results_50.jsonl
- data/interim/grounded_answers_50.jsonl
- evaluation/retrieval/*_metrics.json
- evaluation/retrieval/failure_analysis_50.md
- evaluation/retrieval/urdu_unicode_report.json

This is professional evidence for recruiter / MS admission - Sequence wise PDF stages 083-138 + Part XIII.
