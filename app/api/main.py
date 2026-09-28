from fastapi import FastAPI
from pydantic import BaseModel
import pathlib, json, faiss
from sentence_transformers import SentenceTransformer
import numpy as np

BASE = pathlib.Path(__file__).resolve().parents[2]
INDEX_PATH = BASE / "data/processed/faiss_index/index.faiss"
MAP_PATH = BASE / "data/processed/faiss_index/id_to_chunk.json"

app = FastAPI(title="PAKGOV RAG API - 2111 pages 6711 chunks 6711 vectors")
index = faiss.read_index(str(INDEX_PATH))
with open(MAP_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)
model = SentenceTransformer('all-MiniLM-L6-v2')

class QueryReq(BaseModel):
    query: str
    k: int = 5

@app.get("/")
def root():
    return {"status": "PAKGOV RAG ready", "vectors": index.ntotal, "chunks": len(chunks), "pages": 2111, "hashes": ["c51d194b","08cf1868","bd0caf96","0feb1c0a","e2cd2bb9","4e00b563"]}

@app.post("/query")
def query_api(req: QueryReq):
    q_emb = model.encode([req.query])
    scores, ids = index.search(np.array(q_emb, dtype=np.float32), req.k)
    results = []
    for score, idx in zip(scores[0], ids[0]):
        if idx == -1:
            continue
        c = chunks[idx]
        results.append({"score": float(score), "chunk_id": c["chunk_id"], "source_file": c["source_file"], "text": c["text"]})
    return {"query": req.query, "k": req.k, "results": results}