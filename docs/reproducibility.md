# Reproducing RRF fusion

`app/eval/evaluate_hybrid_rrf.py` fuses the existing ranked BM25 and dense
results with Reciprocal Rank Fusion (`k=60`). It needs:

- `data/interim/bm25_results_50.jsonl`
- `data/interim/dense_results_50.jsonl`
- `evaluation/retrieval/bm25_metrics.json`
- `evaluation/retrieval/dense_metrics.json`

From the repository root, run:

```sh
python app/eval/evaluate_hybrid_rrf.py
```

This writes `data/interim/hybrid_rrf_results_50.jsonl` and
`evaluation/retrieval/hybrid_rrf_metrics.json`. Use a separate checkout or
copies of the inputs when comparing experiments, to preserve earlier outputs.
Fusion itself uses only the Python standard library; it does not load an
embedding model or rebuild either baseline.

Candidates are ordered by decreasing RRF score. Equal scores retain their
first-seen order: BM25 rank order, then dense-only candidates in dense rank
order. This matches the demo's fusion order and makes a fixed pair of input
files produce the same ranking regardless of `PYTHONHASHSEED`.

Before this tie rule, a set's iteration order could change Recall@K and MRR
between runs. Historical committed metrics have not been recomputed as part
of the fix. Changing a tie rule can change which item appears at a cutoff;
compare reruns under the same rule rather than treating that change as a
retriever improvement.

Run the offline regressions with:

```sh
python -m unittest discover -s tests -v
```

The tests use temporary copies, synthetic ties, and the committed baseline
results. They check fusion stability and scoring, not the embedding models,
document relevance, or grounded-answer quality.
