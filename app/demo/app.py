import json, re, unicodedata
from pathlib import Path
import numpy as np
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
PROC = ROOT / "data" / "processed"
MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
RRF_K = 60

st.set_page_config(page_title="PAKGOV-RAG", layout="wide")
st.title("PAKGOV-RAG")
st.caption("Bilingual Urdu-English retrieval over Pakistani legal documents. "
           "Hybrid BM25 + dense (RRF k=60). Extractive answers only, no generated text.")

def clean_source(name):
    n = str(name).replace("PAKISTANCODE__", "")
    n = re.sub(r"\.(txt|pdf)$", "", n)
    return n.replace("_", " ").strip()

@st.cache_data(show_spinner="Loading chunks...")
def load_chunks():
    lines = (PROC / "chunks.jsonl").read_text(encoding="utf-8").splitlines()
    out = []
    for i, l in enumerate(l for l in lines if l.strip()):
        r = json.loads(l)
        out.append({
            "text": unicodedata.normalize("NFC", str(r.get("text", ""))),
            "source": clean_source(r.get("source_file", "unknown")),
            "loc": f"chars {r.get('start_char', '?')}-{r.get('end_char', '?')}",
        })
    return out

chunks = load_chunks()
st.sidebar.write(f"Loaded **{len(chunks)}** chunks")
top_k = st.sidebar.slider("Results", 1, 10, 5)
min_cos = st.sidebar.slider("Min cosine for 'cited' (demo rule)", 0.0, 1.0, 0.20, 0.01)
st.sidebar.caption("Demo rule only. It is not the Part XIII evaluation rule.")

def tok(s):
    return re.findall(r"\w+", unicodedata.normalize("NFC", s).lower())

@st.cache_resource(show_spinner="Building BM25...")
def get_bm25():
    from rank_bm25 import BM25Okapi
    return BM25Okapi([tok(c["text"]) for c in chunks])

@st.cache_resource(show_spinner="Loading model and FAISS index...")
def get_dense():
    import faiss
    from sentence_transformers import SentenceTransformer
    index = faiss.read_index(str(PROC / "faiss_index" / "index.faiss"))
    return SentenceTransformer(MODEL), index

bm25 = get_bm25()
model, index = get_dense()
if index.ntotal != len(chunks):
    st.error(f"FAISS has {index.ntotal} vectors but chunks.jsonl has {len(chunks)}. Order may not match.")
    st.stop()

def unit(v):
    return v / (np.linalg.norm(v) + 1e-9)

def search(q, k):
    qv = unit(model.encode([q])[0].astype("float32"))
    _, d_ids = index.search(qv.reshape(1, -1), 50)
    d_ids = [int(i) for i in d_ids[0] if i >= 0]
    b_scores = bm25.get_scores(tok(q))
    b_ids = [int(i) for i in np.argsort(-b_scores)[:50]]
    fused = {}
    for r, i in enumerate(b_ids, 1):
        fused[i] = fused.get(i, 0) + 1 / (RRF_K + r)
    for r, i in enumerate(d_ids, 1):
        fused[i] = fused.get(i, 0) + 1 / (RRF_K + r)
    top = sorted(fused, key=fused.get, reverse=True)[:k]
    res = []
    for i in top:
        cos = float(unit(index.reconstruct(i).astype("float32")) @ qv)
        res.append((i, fused[i], float(b_scores[i]), cos))
    return res

def best_sentences(q, text, n=2):
    sents = [s.strip() for s in re.split(r"(?<=[.!?۔;:])\s+", text) if len(s.strip()) > 20]
    qt = set(tok(q))
    sents.sort(key=lambda s: len(qt & set(tok(s))), reverse=True)
    return sents[:n] or [text[:300]]

q = st.text_input("Ask a question (English or اردو)",
                  placeholder="What is the Right to Information?  /  آرٹیکل 19 اے کیا ہے؟")
if q:
    hits = search(q, top_k)
    top = chunks[hits[0][0]]
    if max(h[3] for h in hits) < min_cos:
        st.warning("INSUFFICIENT EVIDENCE: no retrieved chunk is similar enough to the question.")
    else:
        st.subheader("Answer (extracted from the top source)")
        for s in best_sentences(q, top["text"]):
            st.write(s + " [1]")
        st.success(f"CITED [1]: {top['source']} | {top['loc']}")
    st.subheader("Retrieved sources")
    for n, (i, rrf, b, cos) in enumerate(hits, 1):
        c = chunks[i]
        with st.expander(f"[{n}] {c['source']} | {c['loc']} | RRF {rrf:.4f}"):
            st.caption(f"BM25 {b:.2f} | dense cosine {cos:.3f}")
            st.write(c["text"])