import pathlib, json
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

BASE = pathlib.Path(__file__).resolve().parents[2]
INDEX_PATH = BASE / "data/processed/faiss_index/index.faiss"
MAP_PATH = BASE / "data/processed/faiss_index/id_to_chunk.json"

print(f"Loading index {INDEX_PATH}")
index = faiss.read_index(str(INDEX_PATH))
with open(MAP_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

model = SentenceTransformer('all-MiniLM-L6-v2')

def retrieve(query: str, k=5):
    q_emb = model.encode([query])
    scores, ids = index.search(np.array(q_emb, dtype=np.float32), k)
    results = []
    for score, idx in zip(scores[0], ids[0]):
        if idx == -1:
            continue
        c = chunks[idx]
        results.append({"score": float(score), "chunk_id": c["chunk_id"], "source_file": c["source_file"], "text": c["text"][:500]})
    return results

if __name__ == "__main__":
    q = "What does Constitution say about fundamental rights?"
    print(f"Query: {q}")
    res = retrieve(q, k=3)
    for r in res:
        print(f"Score {r['score']:.4f} | {r['source_file']} | {r['chunk_id']}")
        print(r['text'][:300])
        print("---")
    print(f"Done - Retrieved {len(res)} chunks from 6711 vectors")