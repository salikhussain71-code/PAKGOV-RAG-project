<div align="center">

# 🇵🇰 PAKGOV-RAG

### Bilingual (Urdu + English) Retrieval-Augmented Generation over the Constitution of Pakistan

*Hybrid retrieval · Citation-grounded answers · Failures reported openly*

[

![olud.ai](https://olud.ai/badge.php?tool=salikhussain71-code-pakgov-rag-project)

](https://olud.ai/project/salikhussain71-code-pakgov-rag-project.html)


![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)




![License](https://img.shields.io/badge/License-MIT-green)




![Stars](https://img.shields.io/github/stars/salikhussain71-code/PAKGOV-RAG-project?style=flat&logo=github)




![Forks](https://img.shields.io/github/forks/salikhussain71-code/PAKGOV-RAG-project?style=flat&logo=github)




![Last Commit](https://img.shields.io/github/last-commit/salikhussain71-code/PAKGOV-RAG-project)





![Chunks](https://img.shields.io/badge/Corpus-6%2C711%20chunks-blue)




![Eval](https://img.shields.io/badge/Eval%20Set-50%20questions-orange)




![R@5](https://img.shields.io/badge/Hybrid%20RRF%20R%405-0.740-brightgreen)




![MRR](https://img.shields.io/badge/Hybrid%20RRF%20MRR-0.605-brightgreen)




![Grounded](https://img.shields.io/badge/Grounded%20Answers-74%25-success)




![Languages](https://img.shields.io/badge/Languages-Urdu%20%7C%20English%20%7C%20Mixed-purple)





![FAISS](https://img.shields.io/badge/FAISS-dense%20search-0467DF)




![BM25](https://img.shields.io/badge/BM25-rank__bm25-lightgrey)




![SBERT](https://img.shields.io/badge/sentence--transformers-5.1.2-orange)




![Streamlit](https://img.shields.io/badge/Streamlit-1.64.0-FF4B4B?logo=streamlit&logoColor=white)




![PyMuPDF](https://img.shields.io/badge/PyMuPDF-pdfplumber-informational)



[**Overview**](#-overview) · [**Results**](#-results) · [**Architecture**](#-architecture) · [**Demo**](#-run-the-demo) · [**Reproduce**](#-reproduce-the-results) · [**Limitations**](#-limitations) · [**Roadmap**](#-roadmap)

</div>

---

## 🎯 Overview

PAKGOV-RAG answers questions about the **Constitution of Pakistan** in **English, Urdu, or a mix of both**.

1. It **retrieves** the most relevant passages.
2. It **generates** an answer only from those passages.
3. It **cites** the source page.
4. If the evidence does not contain the answer, it says **"insufficient evidence"** instead of guessing.

It is also a small, honest study of retrieval quality on a **low-resource language**. Three retrievers are compared on the same question set, and every failure is logged.

### Why this matters

- Government and legal documents are hard for ordinary citizens to search, especially in Urdu.
- Most RAG demos report only their successes. This project publishes its failures too.
- Urdu is under-served by NLP tooling, so measuring where retrieval breaks is useful in itself.

---

## 📊 Results

All numbers come from the **same 50-question evaluation set**, so the comparison is like for like.

| Retriever | R@1 | R@3 | R@5 | R@10 | MRR |
|---|:---:|:---:|:---:|:---:|:---:|
| BM25 (baseline) | 0.360 | 0.580 | 0.640 | 0.680 | 0.469 |
| Dense (multilingual MiniLM) | 0.440 | 0.600 | 0.620 | 0.740 | 0.535 |
| **Hybrid RRF (k=60)** | **0.500** | **0.660** | **0.740** | **0.820** | **0.605** |

**Recall@5 at a glance**

```
BM25    ████████████████░░░░░░░░░  0.640
Dense   ███████████████░░░░░░░░░░  0.620
Hybrid  ██████████████████░░░░░░░  0.740  ← best
```

Hybrid RRF is the strongest on every metric. At R@5 it is **10 points above BM25** and **12 points above dense retrieval**.

### Grounded generation (50 questions)

| Outcome | Count | Share |
|---|:---:|:---:|
| Answer with `[Source: Constitution.pdf p.X]` citation | 37 | 74% |
| `insufficient evidence` returned | 13 | 26% |

The 13 refusals match the 13 questions where the gold source was **not** in the top 5, so the system declines instead of hallucinating.

### Multilingual checks

- Urdu text is **NFC-normalized**
- Embedding shape is `[5, 384]` on the test batch
- Urdu–English cross-lingual similarity on the test pair: **0.8370**

---

## 🧪 Evaluation Set

| Property | Value |
|---|---|
| Questions | 50, with manually verified gold sources |
| English | 15 |
| Urdu | 15 |
| Mixed-language | 20 |
| Corpus | 6,711 chunks from Constitution of Pakistan PDFs, with page and article metadata preserved |

---

## 🏗️ Architecture

```mermaid
flowchart LR
    A[PDF Documents] --> B[Extraction<br/>PyMuPDF / pdfplumber]
    B --> C[Cleaning +<br/>Unicode NFC]
    C --> D[Chunking<br/>page + article metadata]
    D --> E[Embedding<br/>MiniLM-L12 · 384d]
    D --> F[BM25 Index]
    E --> G[FAISS Index]
    Q[User Question<br/>Urdu / English / Mixed] --> F
    Q --> G
    F --> H[Reciprocal Rank Fusion<br/>k=60]
    G --> H
    H --> I{Evidence<br/>found?}
    I -- Yes --> J[Grounded Answer<br/>+ Page Citation]
    I -- No --> K[Insufficient Evidence]
```

| Stage | Implementation |
|---|---|
| Ingestion | PDF text extraction (PyMuPDF / pdfplumber), cleaning, Unicode NFC normalization |
| Chunking | 6,711 chunks with page and article metadata |
| Embedding | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 dimensions) |
| Lexical retrieval | BM25 (`rank_bm25`) |
| Dense retrieval | FAISS |
| Fusion | Reciprocal Rank Fusion, k=60 |
| Generation | Answers built only from retrieved chunks, with page citations |
| Evaluation | Recall@1/3/5/10 and MRR on the fixed 50-question set |

---

## 🛠️ Tech Stack

`Python 3.14` · `sentence-transformers 5.1.2` · `FAISS` · `rank_bm25` · `Streamlit 1.64.0` · `PyMuPDF` · `pdfplumber`

---

## ▶️ Run the Demo

```bash
pip install streamlit sentence-transformers faiss-cpu rank_bm25
python -m streamlit run app/demo/app.py --server.port 8501
```

Open **http://localhost:8501**

**Example queries**

```
What is Right to Information?
Article 19A
آرٹیکل 19 اے کیا ہے؟
```

Each result shows the question, detected language, status (`grounded` or `insufficient evidence`), the answer, and its citation.

---

## 🔁 Reproduce the Results

```bash
python app/eval/final_table.py
```

This regenerates the results table and writes `evaluation/retrieval/FINAL_RESULTS.md`.

### Repository evidence

Raw evaluation outputs are committed so the numbers can be checked directly.

```
data/interim/
├── bm25_results_50.jsonl
├── dense_results_50.jsonl
├── hybrid_rrf_results_50.jsonl
└── grounded_answers_50.jsonl

evaluation/retrieval/
├── bm25_metrics_50.json
├── dense_metrics_50.json
├── hybrid_rrf_metrics_50.json
├── grounded_metrics.json
├── failure_analysis_50.md
├── urdu_unicode_report.json
└── FINAL_RESULTS.md

app/
├── demo/app.py
└── eval/final_table.py
```

---

## 🏛️ Senate Extension (1–2 Oct 2026)

Extended the pipeline to **10 official PDFs** from [senate.gov.pk](https://www.senate.gov.pk/en/rules.php) (Publications → Rules and Acts), saved in `data/raw/senate/`.

| File | Pages | Status |
|---|:---:|---|
| Rules_Procedure_Conduct_Business_Senate_2012_2026 | 111 | ✅ readable |
| Constitution_Pakistan_2025_11_14 | 176 | ✅ readable |
| Chairman_Speaker_Salaries_Act_1975 | 11 | ✅ readable |
| Dy_Chairman_Dy_Speaker_Salaries_Act_1975 | 11 | ✅ readable |
| Enhancement_Role_Powers_Senate_2017 | 32 | ✅ readable |
| Members_Parliament_Salaries_Act_1974_Medical_Rules_1990 | 44 | ✅ readable |
| Senate_Secretariat_Service_Act_2017 | 15 | ✅ readable |
| Senate_Secretariat_Service_Rules_2021 | 26 | ✅ readable (low text yield) |
| Parliament_Joint_Sittings_Rules_1973 | 23 | ⏳ scanned, OCR (Tesseract) pending |
| Senate_Finance_Committee_Rules_1973 | 10 | ⏳ scanned, OCR (Tesseract) pending |

**Pipeline run**

```bash
python ingestion/extract.py --input data/raw/senate --output data/interim/senate_raw.jsonl
python ingestion/chunking/chunk_documents.py --input data/interim/senate_raw.jsonl --output data/processed/senate_chunks.jsonl
python retrieval/embed.py --input data/processed/senate_chunks.jsonl --output data/processed/senate_faiss
```

**Outcome:** 10 PDFs processed, 2 scanned PDFs handled without crashing, **1,080 chunks** saved, and a FAISS index built with **1,080 vectors**.

*Source: Senate of Pakistan, © 2019–2026.*

---

## ⚠️ Limitations

- **Small evaluation set.** With 50 questions, one question is worth 2 points. A 10-point gap at R@5 is 5 questions, so treat the ranking as indicative, not definitive.
- **Single corpus.** Main results are for the Constitution only and may not carry over to other legal or government documents.
- **Failures are real.** 13 of 50 questions (26%) miss at R@5. The system refuses rather than hallucinates, but it does not yet recover them. See `evaluation/retrieval/failure_analysis_50.md`.
- **Lightweight embedding model.** MiniLM-L12 is fast but not the strongest option for Urdu. Larger multilingual encoders and rerankers are the obvious next step.

---

## 🗺️ Roadmap

- [x] BM25 / Dense / Hybrid RRF comparison on 50 questions
- [x] Citation-grounded generation with refusal on weak evidence
- [x] Streamlit demo
- [x] Senate documents ingested, chunked, and embedded (1,080 chunks)
- [ ] OCR (Tesseract) for the 2 scanned Senate PDFs
- [ ] Larger, more varied evaluation set
- [ ] Stronger multilingual embeddings and a cross-encoder reranker
- [ ] Article-aware chunking to reduce retrieval misses
- [ ] Extension to other Pakistani government documents

---

## 👤 Author

**Salik Hussain**
Research interest: **Urdu NLP and low-resource language AI**

[

![GitHub](https://img.shields.io/badge/GitHub-salikhussain71--code-181717?logo=github)

](https://github.com/salikhussain71-code)
[

![Email](https://img.shields.io/badge/Email-salikhussain71%40gmail.com-D14836?logo=gmail&logoColor=white)

](mailto:salikhussain71@gmail.com)

## 📄 License

MIT License. Copyright (c) 2026 Salik Hussain. See [LICENSE](LICENSE).

---

<div align="center">

⭐ If this project helps your research, please star the repo.

</div>