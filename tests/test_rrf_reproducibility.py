import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "app" / "eval" / "evaluate_hybrid_rrf.py"


class RRFReproducibilityTests(unittest.TestCase):
    def run_rrf(self, bm25_rows, dense_rows, seed):
        # The evaluator writes results and metrics relative to its working
        # directory. Isolate every run so committed research outputs stay intact.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data/interim").mkdir(parents=True)
            (root / "evaluation/retrieval").mkdir(parents=True)
            for method, rows in [("bm25", bm25_rows), ("dense", dense_rows)]:
                (root / f"data/interim/{method}_results_50.jsonl").write_text(
                    "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
                )
                (root / f"evaluation/retrieval/{method}_metrics.json").write_text(
                    json.dumps({"recall_at_k": {"5": 1.0}, "mrr": 1.0}),
                    encoding="utf-8",
                )
            result = subprocess.run(
                [sys.executable, str(SCRIPT)],
                cwd=root,
                env=dict(os.environ, PYTHONHASHSEED=str(seed)),
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            rows = [
                json.loads(line)
                for line in (root / "data/interim/hybrid_rrf_results_50.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            ]
            metrics = json.loads(
                (root / "evaluation/retrieval/hybrid_rrf_metrics.json").read_text(
                    encoding="utf-8"
                )
            )
            return rows, metrics

    def row(self, ids):
        return {
            "id": "fixture",
            "question": "Synthetic retrieval question",
            "lang": "en",
            "gold_source_file": "alpha.pdf",
            "gold_page": 1,
            "retrieved_chunk_ids": ids,
            "retrieved_sources": [f"{cid}.pdf" for cid in ids],
        }

    def test_equal_scores_follow_first_seen_order_across_hash_seeds(self):
        bm25 = [self.row(["alpha", "beta"])]
        dense = [self.row(["beta", "alpha"])]
        expected_score = 1 / 61 + 1 / 62
        for seed in [0, 1, 2, 3]:
            with self.subTest(seed=seed):
                rows, metrics = self.run_rrf(bm25, dense, seed)
                self.assertEqual(rows[0]["retrieved_chunk_ids"], ["alpha", "beta"])
                self.assertEqual(rows[0]["retrieved_sources"], ["alpha.pdf", "beta.pdf"])
                self.assertEqual(rows[0]["scores"], [expected_score, expected_score])
                self.assertEqual(metrics["recall_at_k"]["1"], 1.0)
                self.assertEqual(metrics["mrr"], 1.0)

    def test_unequal_scores_still_determine_the_ranking(self):
        rows, _ = self.run_rrf(
            [self.row(["alpha", "beta", "gamma"])],
            [self.row(["gamma", "alpha", "delta"])],
            1,
        )
        self.assertEqual(
            rows[0]["retrieved_chunk_ids"], ["alpha", "gamma", "beta", "delta"]
        )
        self.assertEqual(
            rows[0]["scores"], [1 / 61 + 1 / 62, 1 / 63 + 1 / 61, 1 / 62, 1 / 63]
        )

    def test_committed_baseline_inputs_produce_the_same_results_across_seeds(self):
        inputs = []
        for method in ["bm25", "dense"]:
            inputs.append([
                json.loads(line)
                for line in (ROOT / f"data/interim/{method}_results_50.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
                if line.strip()
            ])
        first = self.run_rrf(*inputs, seed=0)
        second = self.run_rrf(*inputs, seed=1)
        self.assertEqual(first, second)
        self.assertEqual(len(first[0]), 50)


if __name__ == "__main__":
    unittest.main()
