<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f2027,50:203a43,100:2c5364&height=200&section=header&text=PAKGOV-RAG&fontSize=60&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Urdu%20%2B%20English%20RAG%20for%20Pakistani%20Legal%20Documents&descAlignY=60&descSize=18" alt="PAKGOV-RAG banner" width="100%">

<img src="https://github.com/salikhussain71-code.png" width="110" alt="Salik Hussain" style="border-radius:50%">

<a href="https://github.com/salikhussain71-code/PAKGOV-RAG-project">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=20&pause=1200&color=22C55E&center=true&vCenter=true&width=720&lines=Hybrid+BM25+%2B+Dense+Retrieval+(RRF);Urdu+%2B+English+%2B+Mixed+Queries;Citation-Grounded+Answers;Failures+Reported+Openly" alt="Typing animation">
</a>

### Bilingual (Urdu + English) Retrieval-Augmented Generation over Pakistani Government & Legal Documents

*Hybrid retrieval · Citation-grounded answers · Failures reported openly*

<!-- ROW 1: recognition + repo status -->
<p align="center">
  <a href="https://olud.ai/project/salikhussain71-code-pakgov-rag-project.html"><img src="https://olud.ai/badge.php?tool=salikhussain71-code-pakgov-rag-project" alt="olud.ai"></a>
  <img src="https://img.shields.io/badge/XERJ%20Corpus%20Hub-Selected%20%7C%20Attributed-gold?logo=databricks&logoColor=white" alt="XERJ Corpus Hub">
  <img src="https://img.shields.io/badge/Status-Active%20Research-blueviolet" alt="Status">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white" alt="Python">
</p>

<!-- ROW 2: live GitHub stats -->
<p align="center">
  <img src="https://img.shields.io/github/stars/salikhussain71-code/PAKGOV-RAG-project?style=flat&logo=github" alt="Stars">
  <img src="https://img.shields.io/github/forks/salikhussain71-code/PAKGOV-RAG-project?style=flat&logo=github" alt="Forks">
  <img src="https://img.shields.io/github/last-commit/salikhussain71-code/PAKGOV-RAG-project" alt="Last Commit">
  <img src="https://img.shields.io/github/repo-size/salikhussain71-code/PAKGOV-RAG-project" alt="Repo Size">
  <img src="https://img.shields.io/github/languages/top/salikhussain71-code/PAKGOV-RAG-project" alt="Top Language">
</p>

<!-- ROW 3: results -->
<p align="center">
  <img src="https://img.shields.io/badge/Corpus-6%2C711%20chunks-blue" alt="Corpus">
  <img src="https://img.shields.io/badge/Eval%20Set-50%20questions-orange" alt="Eval">
  <img src="https://img.shields.io/badge/Hybrid%20RRF%20R%405-0.740-brightgreen" alt="R@5">
  <img src="https://img.shields.io/badge/Hybrid%20RRF%20MRR-0.605-brightgreen" alt="MRR">
  <img src="https://img.shields.io/badge/Grounded%20Answers-74%25-success" alt="Grounded">
</p>

<!-- ROW 4: language + focus -->
<p align="center">
  <img src="https://img.shields.io/badge/Languages-Urdu%20%7C%20English%20%7C%20Mixed-purple" alt="Languages">
  <img src="https://img.shields.io/badge/Focus-Urdu%20NLP%20%7C%20Low--Resource%20AI-teal" alt="Focus">
  <img src="https://img.shields.io/badge/Answers-Extractive%20%7C%20Cited-informational" alt="Answers">
</p>

<!-- ROW 5: tech stack -->
<p align="center">
  <img src="https://img.shields.io/badge/FAISS-dense%20search-0467DF" alt="FAISS">
  <img src="https://img.shields.io/badge/BM25-rank__bm25-lightgrey" alt="BM25">
  <img src="https://img.shields.io/badge/sentence--transformers-5.1.2-orange" alt="SBERT">
  <img src="https://img.shields.io/badge/Streamlit-1.64.0-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/PyMuPDF-pdfplumber-informational" alt="PyMuPDF">
</p>

<!-- ROW 6: navigation -->
<p align="center">
  <a href="#-live-demo"><b>Demo</b></a> ·
  <a href="#-open-source-recognition"><b>Recognition</b></a> ·
  <a href="#-results"><b>Results</b></a> ·
  <a href="#-project-status-done-vs-remaining"><b>Done vs Remaining</b></a> ·
  <a href="#-architecture"><b>Architecture</b></a> ·
  <a href="#-reproduce-the-results"><b>Reproduce</b></a> ·
  <a href="#-limitations"><b>Limitations</b></a> ·
  <a href="#-roadmap"><b>Roadmap</b></a> ·
  <a href="#-author"><b>Author</b></a>
</p>

</div>

---

## 🖼️ Live Demo

<p align="center">
  <img src="docs/demo.png" alt="PAKGOV-RAG Streamlit demo answering 'Article 19A' with a cited source" width="900">
</p>
<p align="center"><em>Query "Article 19A" returns an extracted answer, its citation, and the top 5 retrieved sources with RRF scores.</em></p>

---

## ⚡ At a Glance

| 📚 Corpus | 🧪 Eval Set | 🎯 Best R@5 | 📈 Best MRR | ✅ Grounded | 🌐 Languages |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **6,711** chunks | **50** questions | **0.740** | **0.605** | **74%** | **3** (UR / EN / mixed) |

---

## 🏅 Open-Source Recognition

| 🌐 Listed On | 🏆 Recognition |
|:---:|:---|
| **olud.ai** | PAKGOV-RAG is listed in the olud.ai AI project directory. |
| **XERJ Corpus Hub** | PAKGOV-RAG was selected for the indexed corpus hub, with attribution. |

<p align="center">
  <a href="https://olud.ai/project/salikhussain71-code-pakgov-rag-project.html"><img src="https://olud.ai/badge.php?tool=salikhussain71-code-pakgov-rag-project" alt="olud.ai"></a>
  <img src="https://img.shields.io/badge/Directory-Listed%20on%20olud.ai-blueviolet?logo=starship&logoColor=white" alt="Listed">
  <img src="https://img.shields.io/badge/XERJ%20Corpus%20Hub-Selected%20%7C%20Attributed-gold?logo=databricks&logoColor=white" alt="XERJ">
  <img src="https://img.shields.io/badge/Open%20Source-MIT-green?logo=opensourceinitiative&logoColor=white" alt="Open Source">
</p>

> 💬 *Independent platforms have indexed and credited this project, which makes it easier for other researchers to find and verify the work.*

---

## 🎯 Overview

PAKGOV-RAG answers questions about the **Constitution of Pakistan** in **English, Urdu, or a mix of both**.

1. It **retrieves** the most relevant passages (BM25 + dense, fused with RRF).
2. It **extracts** the answer only from retrieved passages, with no free-form generation.
3. It **cites** the source passage.
4. If the evidence does not contain the answer, it says **"insufficient evidence"** instead of guessing.

It is also a small, honest study of retrieval quality on a **low-resource language**. Three retrievers are compared on the same question set, and every failure is logged.

### 💡 Why this matters

- Government and legal documents are hard for ordinary citizens to search, especially in Urdu.
- Most RAG demos report only their successes. This project publishes its failures too.
- Urdu is under-served by NLP tooling, so measuring where retrieval breaks is useful in itself.

### ⭐ Project Highlights

| 🔎 Hybrid search | 🛡️ No guessing | 🧾 Fully reproducible | 🌍 Low-resource focus |
|:---:|:---:|:---:|:---:|
| BM25 + dense fused with RRF beats both alone | Refuses when evidence is missing | Raw outputs committed, one command regenerates results | Urdu, English and mixed queries |

---

## 📊 Results

All numbers come from the **same 50-question evaluation set**, so the comparison is like for like.

| Retriever | R@1 | R@3 | R@5 | R@10 | MRR |
|---|:---:|:---:|:---:|:---:|:---:|
| BM25 (baseline) | 0.360 | 0.580 | 0.640 | 0.680 | 0.469 |
| Dense (multilingual MiniLM) | 0.440 | 0.600 | 0.620 | 0.740 | 0.535 |
| **Hybrid RRF (k=60)** | **0.500** | **0.660** | **0.740** | **0.820** | **0.605** |

**Recall@5**

```
BM25    ████████████████░░░░░░░░░  0.640
Dense   ███████████████░░░░░░░░░░  0.620
Hybrid  ██████████████████░░░░░░░  0.740  ← best
```

**MRR**

```
BM25    ███████████░░░░░░░░░░░░░░  0.469
Dense   █████████████░░░░░░░░░░░░  0.535
Hybrid  ███████████████░░░░░░░░░░  0.605  ← best
```

### 🔑 Key findings

- Hybrid RRF is the strongest on **every metric**.
- At R@5 it is **10 points above BM25** and **12 points above dense retrieval**.
- BM25 and dense fail on different questions, and fusing them recovers many of those misses.

### 🛡️ Grounded answers (50 questions)

| Outcome | Count | Share |
|---|:---:|:---:|
| Answer with `[Source: Constitution.pdf p.X]` citation | 37 | 74% |
| `insufficient evidence` returned | 13 | 26% |

The 13 refusals match the 13 questions where the gold source was **not** in the top 5, so the system declines instead of hallucinating.

### 🌐 Multilingual checks

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

## ✅ Project Status: Done vs Remaining

**Overall:** the core research pipeline and evaluation are complete. Current work is extending to more documents and improving retrieval quality.

```
Core pipeline & evaluation   ████████████████████  DONE
Demo application             ████████████████████  DONE
Senate corpus extension      ██████████████░░░░░░  IN PROGRESS (8 of 10 PDFs readable)
Retrieval improvements       ████░░░░░░░░░░░░░░░░  PLANNED
```

### ✅ Done

| Area | What was completed |
|---|---|
| **Ingestion** | PDF text extraction with PyMuPDF / pdfplumber, cleaning, Unicode NFC normalization |
| **Chunking** | 6,711 chunks with page and article metadata preserved |
| **Embeddings** | `paraphrase-multilingual-MiniLM-L12-v2`, 384 dimensions |
| **Retrieval** | BM25 baseline, dense FAISS search, and Hybrid RRF (k=60) |
| **Evaluation** | 50 questions (15 EN / 15 UR / 20 mixed) with manually verified gold sources; Recall@1/3/5/10 and MRR |
| **Grounded answers** | Extractive answers with citations; `insufficient evidence` when support is missing |
| **Failure analysis** | All 13 R@5 misses logged in `failure_analysis_50.md` |
| **Reproducibility** | Raw `.jsonl` results and `.json` metrics committed; one command regenerates the table |
| **Demo** | Streamlit app with adjustable result count and citation threshold |
| **Senate extension** | 10 official PDFs downloaded, extracted, chunked (1,080 chunks), and indexed (1,080 FAISS vectors) |
| **Robustness** | 2 scanned PDFs handled without crashing the pipeline |
| **Open-source setup** | MIT license, contributing guide, security policy |
| **Recognition** | Listed on olud.ai; selected for the XERJ Corpus Hub with attribution |

### 🔜 Remaining

| Priority | Task | Why it matters |
|:---:|---|---|
| 🔴 High | **OCR the 2 scanned Senate PDFs** (Tesseract) | Joint Sittings Rules 1973 and Finance Committee Rules 1973 currently contribute only placeholder text |
| 🔴 High | **Larger, more varied evaluation set** | 50 questions means one question is worth 2 points; more questions make the ranking reliable |
| 🔴 High | **Evaluate on the Senate corpus** | Shows whether results carry beyond the Constitution |
| 🟠 Medium | **Cross-encoder reranker** | Targets the 13 questions that miss at R@5 |
| 🟠 Medium | **Stronger multilingual embeddings** | MiniLM-L12 is fast but not the strongest option for Urdu |
| 🟠 Medium | **Article-aware chunking** | Keeps each article intact to reduce retrieval misses |
| 🟡 Planned | **Fix the low text yield** in `Senate_Secretariat_Service_Rules_2021` (26 pages, only 3,286 chars) | Likely partial scan or extraction issue |
| 🟡 Planned | **Unified index** across the Constitution and Senate documents | One search over all documents |
| 🟡 Planned | **Public deployment** of the demo | Lets anyone try it without installing |
| 🟡 Planned | **Short write-up / paper** on Urdu legal retrieval | Turns the evaluation into a citable result |

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
    I -- Yes --> J[Extracted Answer<br/>+ Citation]
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
| Answering | Extractive: answers come only from retrieved chunks, with citations |
| Evaluation | Recall@1/3/5/10 and MRR on the fixed 50-question set |

---

## 🛠️ Tech Stack

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-1.64.0-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/FAISS-Vector%20Search-0467DF?style=for-the-badge" alt="FAISS">
  <img src="https://img.shields.io/badge/BM25-rank__bm25-555555?style=for-the-badge" alt="BM25">
  <img src="https://img.shields.io/badge/SBERT-5.1.2-F59E0B?style=for-the-badge" alt="SBERT">
  <img src="https://img.shields.io/badge/PyMuPDF-PDF%20Parsing-22C55E?style=for-the-badge" alt="PyMuPDF">
  <img src="https://img.shields.io/badge/pdfplumber-PDF%20Parsing-8B5CF6?style=for-the-badge" alt="pdfplumber">
</p>

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
| Senate_Secretariat_Service_Rules_2021 | 26 | ⚠️ readable, low text yield |
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
- **Single main corpus.** Main results are for the Constitution only and may not carry over to other legal or government documents.
- **Failures are real.** 13 of 50 questions (26%) miss at R@5. The system refuses rather than hallucinates, but it does not yet recover them. See `evaluation/retrieval/failure_analysis_50.md`.
- **Lightweight embedding model.** MiniLM-L12 is fast but not the strongest option for Urdu. Larger multilingual encoders and rerankers are the obvious next step.
- **Extractive only.** Answers are pulled from the top source, not synthesized across several sources.

---

## 🗺️ Roadmap

- [x] BM25 / Dense / Hybrid RRF comparison on 50 questions
- [x] Citation-grounded answers with refusal on weak evidence
- [x] Failure analysis published
- [x] Streamlit demo
- [x] Senate documents ingested, chunked, and embedded (1,080 chunks)
- [x] Listed on olud.ai and selected for the XERJ Corpus Hub
- [ ] OCR (Tesseract) for the 2 scanned Senate PDFs
- [ ] Larger, more varied evaluation set
- [ ] Evaluation on the Senate corpus
- [ ] Cross-encoder reranker
- [ ] Stronger multilingual embeddings
- [ ] Article-aware chunking
- [ ] Unified index across all documents
- [ ] Public deployment
- [ ] Short write-up on Urdu legal retrieval

---

## 🎓 Skills Demonstrated

| Area | Evidence in this repo |
|---|---|
| **Information retrieval** | BM25, dense retrieval, Reciprocal Rank Fusion |
| **NLP for low-resource languages** | Urdu NFC normalization, cross-lingual similarity checks |
| **Evaluation methodology** | Fixed question set, Recall@k and MRR, honest failure analysis |
| **Data engineering** | PDF extraction, scanned-PDF handling, chunking with metadata |
| **Reproducible research** | Committed raw outputs, one-command result regeneration |
| **Applied ML engineering** | FAISS indexing, sentence-transformers, Streamlit app |

---

## 📈 Star History

<p align="center">
  <a href="https://star-history.com/#salikhussain71-code/PAKGOV-RAG-project&Date">
    <img src="https://api.star-history.com/svg?repos=salikhussain71-code/PAKGOV-RAG-project&type=Date" alt="Star History Chart" width="600">
  </a>
</p>

---

## 👤 Author

<p align="center">
  <img src="https://github.com/salikhussain71-code.png" width="90" alt="Salik Hussain" style="border-radius:50%">
</p>

<p align="center">
  <b>Salik Hussain</b><br>
  Research interest: <b>Urdu NLP and low-resource language AI</b>
</p>

<p align="center">
  <a href="https://github.com/salikhussain71-code"><img src="https://img.shields.io/badge/GitHub-salikhussain71--code-181717?style=for-the-badge&logo=github" alt="GitHub"></a>
  <a href="mailto:salikhussain71@gmail.com"><img src="https://img.shields.io/badge/Email-salikhussain71%40gmail.com-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Email"></a>
</p>

## 📄 License

MIT License. Copyright (c) 2026 Salik Hussain. See [LICENSE](LICENSE).

---

<div align="center">

⭐ If this project helps your research, please star the repo.

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:2c5364,50:203a43,100:0f2027&height=120&section=footer" alt="footer" width="100%">

</div>
