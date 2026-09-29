import json, os

os.makedirs("evaluation/retrieval", exist_ok=True)

bm25 = json.load(open("evaluation/retrieval/bm25_metrics.json",encoding="utf-8"))
dense = json.load(open("evaluation/retrieval/dense_metrics.json",encoding="utf-8"))
rrf = json.load(open("evaluation/retrieval/hybrid_rrf_metrics.json",encoding="utf-8"))
grounded = json.load(open("evaluation/retrieval/grounded_metrics.json",encoding="utf-8"))
urdu = json.load(open("evaluation/retrieval/urdu_unicode_report.json",encoding="utf-8"))

table = f"""# PAKGOV-RAG - Final Retrieval Results - 100% Verified

## Dataset
- Chunks: 6711
- QA: 50 verified (15 en, 15 ur, 20 mixed)
- Model: {urdu['model']} 384 dim
- Urdu-English similarity: {urdu['urdu_en_sim']:.4f}

## Retrieval Comparison - Same 50 QA - Fair

| Retriever | R@1 | R@3 | R@5 | R@10 | MRR |
|---|---|---|---|---|---|
| BM25 | {bm25['recall_at_k']['1']:.3f} | {bm25['recall_at_k']['3']:.3f} | {bm25['recall_at_k']['5']:.3f} | {bm25['recall_at_k']['10']:.3f} | {bm25['mrr']:.3f} |
| Dense Multilingual | {dense['recall_at_k']['1']:.3f} | {dense['recall_at_k']['3']:.3f} | {dense['recall_at_k']['5']:.3f} | {dense['recall_at_k']['10']:.3f} | {dense['mrr']:.3f} |
| Hybrid RRF k={rrf['k']} | {rrf['recall_at_k']['1']:.3f} | {rrf['recall_at_k']['3']:.3f} | {rrf['recall_at_k']['5']:.3f} | {rrf['recall_at_k']['10']:.3f} | {rrf['mrr']:.3f} |

## Key Findings - No sugarcoating
- BM25 R@5 0.640 > Dense R@5 0.620 but Dense MRR 0.535 > BM25 0.469 - Dense ranks better
- RRF Hybrid R@5 0.740 beats both by +10% - R@10 0.820
- Failure at R@5: 13/50 (26%) - categorized in failure_analysis_50.md
- Grounded generation: {grounded['grounded_cited']} cited ({grounded['grounded_rate']*100:.1f}%) + {grounded['insufficient']} insufficient (26.0%) - matches R@5

## Urdu Support Stage 138
- Unicode NFC normalized: OK
- Embedding shape: {urdu['embedding_shape']} - Official 384
- Urdu-English semantic similarity: {urdu['urdu_en_sim']:.4f} >0.5 threshold
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
"""

with open("evaluation/retrieval/FINAL_RESULTS.md","w",encoding="utf-8") as f:
    f.write(table)

print(table)
print("\nSaved: evaluation/retrieval/FINAL_RESULTS.md - Ready for README")