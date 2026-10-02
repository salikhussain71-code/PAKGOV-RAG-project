# PAKGOV-RAG

**Bilingual (Urdu + English) Retrieval-Augmented Generation over the Constitution of Pakistan**

Hybrid retrieval (BM25 + dense embeddings fused with Reciprocal Rank Fusion), citation-grounded answers, and an evaluation that reports failures openly.

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Chunks](https://img.shields.io/badge/Chunks-6711-green)
![QA](https://img.shields.io/badge/Eval%20QA-50-orange)
![RRF R@5](https://img.shields.io/badge/RRF%20R%405-0.740-success)
![RRF MRR](https://img.shields.io/badge/RRF%20MRR-0.605-success)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## Overview

PAKGOV-RAG answers questions about the Constitution of Pakistan in English, Urdu, or a mix of both. It retrieves relevant passages, generates an answer only from those passages, and cites the source page. When the retrieved evidence does not contain the answer, it says so instead of guessing.

The project is also a small, honest study of retrieval quality on a low-resource language: three retrievers are compared on the same question set, and every failure is logged.

## Results

All numbers below come from the same 50-question evaluation set, so the comparison is like for like.

| Retriever | R@1 | R@3 | R@5 | R@10 | MRR |
| :--- | :--- | :--- | :--- | :--- | :--- |
| BM25 (baseline) | 0.360 | 0.580 | 0.640 | 0.680 | 0.469 |
| Dense (multilingual MiniLM) | 0.440 | 0.600 | 0.620 | 0.740 | 0.535 |
| **Hybrid RRF (k=60)** | **0.500** | **0.660** | **0.740** | **0.820** | **0.605** |

Hybrid RRF is the strongest on every metric. At R@5 it is 10 points above BM25 and 12 points above dense retrieval.

**Grounded generation (50 questions)**

- 37 answers (74%) returned with a `[Source: Constitution.pdf p.X]` citation
- 13 answers (26%) returned `insufficient evidence`, matching the 13 questions where the gold source was not in the top 5

**Multilingual checks**

- Urdu text is NFC-normalized
- Embedding shape is `[5, 384]` on the test batch
- Urdu–English cross-lingual similarity on the test pair: 0.8370

## Evaluation Set

- 50 questions with manually verified gold sources
- 15 English, 15 Urdu, 20 mixed-language
- Corpus: 6,711 chunks extracted from Constitution of Pakistan PDFs, with page and article metadata preserved

## Limitations

- **Small evaluation set.** With 50 questions, one question is worth 2 points. A 10-point gap at R@5 is 5 questions, so treat the ranking as indicative rather than definitive.
- **Single corpus.** Results are for the Constitution only and may not carry over to other legal or government documents.
- **Failures are real.** 13 of 50 questions (26%) miss at R@5. The system refuses to answer these rather than hallucinate, but it does not yet recover them. See `evaluation/retrieval/failure_analysis_50.md`.
- **Lightweight embedding model.** MiniLM-L12 is fast but not the strongest option for Urdu. Larger multilingual encoders and rerankers are the obvious next step.

## Architecture

1. **Ingestion:** PDF text extraction (PyMuPDF / pdfplumber), cleaning, Unicode NFC normalization
2. **Chunking:** 6,711 chunks with page and article metadata
3. **Embedding:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 dimensions)
4. **Retrieval:**
   - BM25 lexical search (`rank_bm25`)
   - Dense semantic search (FAISS)
   - Reciprocal Rank Fusion, k=60
5. **Generation:** answers built only from retrieved chunks, with page citations; `insufficient evidence` when support is missing
6. **Evaluation:** Recall@1/3/5/10 and MRR on the fixed 50-question set

## Tech Stack

Python 3.14 · sentence-transformers 5.1.2 · FAISS · rank_bm25 · Streamlit 1.64.0 · PyMuPDF · pdfplumber

## Run the Demo

```bash
pip install streamlit sentence-transformers faiss-cpu rank_bm25
python -m streamlit run app/demo/app.py --server.port 8501
```

Open `http://localhost:8501`.

Example queries:

- `What is Right to Information?`
- `Article 19A`
- `آرٹیکل 19 اے کیا ہے؟`

Each result shows the question, detected language, status (grounded or insufficient evidence), the answer, and its citation.

## Reproduce the Results

```bash
python app/eval/final_table.py
```

This regenerates the results table and writes `evaluation/retrieval/FINAL_RESULTS.md`.

## Repository Evidence

Raw outputs from the evaluation runs are committed so the numbers can be checked directly.

```text
data/interim/
  bm25_results_50.jsonl
  dense_results_50.jsonl
  hybrid_rrf_results_50.jsonl
  grounded_answers_50.jsonl

evaluation/retrieval/
  bm25_metrics_50.json
  dense_metrics_50.json
  hybrid_rrf_metrics_50.json
  grounded_metrics.json
  failure_analysis_50.md
  urdu_unicode_report.json
  FINAL_RESULTS.md

app/
  demo/app.py
  eval/final_table.py
```

## Roadmap

- Larger, more varied evaluation set
- Stronger multilingual embeddings and a cross-encoder reranker
- Article-aware chunking to reduce retrieval misses
- Extension to other Pakistani government documents
## Senate Extension - 10 PDFs Official senate.gov.pk - 1-2 Oct 2026

**Official Source:** https://www.senate.gov.pk/en/rules.php - Publications -> Rules and Acts - Copyright 2019-2026 Senate of Pakistan

### PDFs Downloaded - data/raw/senate/ - 10 files official:
- Rules_Procedure_Conduct_Business_Senate_2012_2026.pdf - 111 pages - 219683 chars - Updated 6 Feb 2026
- Constitution_Pakistan_2025_11_14.pdf - 176 pages - 454525 chars - Updated 14 Nov 2025
- Chairman_Speaker_Salaries_Act_1975.pdf - 11 pages - 28231 chars
- Dy_Chairman_Dy_Speaker_Salaries_Act_1975.pdf - 11 pages - 26020 chars
- Enhancement_Role_Powers_Senate_2017.pdf - 32 pages - 34908 chars
- Members_Parliament_Salaries_Act_1974_Medical_Rules_1990.pdf - 44 pages - 66423 chars
- Parliament_Joint_Sittings_Rules_1973.pdf - 23 pages - SCANNED 0 chars original - Placeholder 198 chars - OCR via Tesseract pending
- Senate_Finance_Committee_Rules_1973.pdf - 10 pages - SCANNED 0 chars original - Placeholder 197 chars - OCR pending
- Senate_Secretariat_Service_Act_2017.pdf - 15 pages - 25532 chars
- Senate_Secretariat_Service_Rules_2021.pdf - 26 pages - 3286 chars

### Pipeline - Commands Executed - Evidence:
```bash
python ingestion/extract.py --input data/raw/senate --output data/interim/senate_raw.jsonl
# Total 10 PDFs saved - 2 scanned PDFs handled without crash - 8 readable + 2 placeholder

python ingestion/chunking/chunk_documents.py --input data/interim/senate_raw.jsonl --output data/processed/senate_chunks.jsonl
# Saved 1080 chunks

python retrieval/embed.py --input data/processed/senate_chunks.jsonl --output data/processed/senate_faiss
# Loading model paraphrase-multilingual-MiniLM-L12-v2 for 1080 chunks...
# Loading weights: 100% 199/199 [00:01, 118.24it/s]
# Batches: 100% 34/34 [04:43]
# Saved FAISS index with 1080 vectors

## Author

**Salik Hussain**
Email: salikhussain71@gmail.com
GitHub: [@salikhussain71-code](https://github.com/salikhussain71-code)
Repository: [PAKGOV-RAG-project](https://github.com/salikhussain71-code/PAKGOV-RAG-project)

Research interest: Urdu NLP and low-resource language AI.

## License

MIT License. Copyright (c) 2026 Salik Hussain.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
