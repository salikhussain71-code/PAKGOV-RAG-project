import pathlib, json, os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

processed_dir = pathlib.Path("data/processed")
chunks_path = processed_dir / "chunks.jsonl"
index_dir = pathlib.Path("data/processed/faiss_index")
index_dir.mkdir(parents=True, exist_ok=True)

print(f"Loading chunks from {chunks_path}")
chunks = []
with chunks_path.open("r", encoding="utf-8") as f:
    for line in f:
        chunks.append(json.loads(line))

texts = [c["text"] for c in chunks]
print(f"{len(texts)} chunks loaded - Example len {len(texts[0])}")

model = SentenceTransformer('all-MiniLM-L6-v2')
print("Encoding 6711 chunks to embeddings...")
embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
print(f"Embeddings shape {embeddings.shape}")

dim = embeddings.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(np.array(embeddings, dtype=np.float32))

faiss.write_index(index, str(index_dir / "index.faiss"))
print(f"FAISS index saved to {index_dir / 'index.faiss'} - {index.ntotal} vectors")

# Save mapping id -> chunk metadata for retrieval
with open(index_dir / "id_to_chunk.json", "w", encoding="utf-8") as out:
    json.dump(chunks, out, ensure_ascii=False, indent=2)

print(f"Done - {len(chunks)} embeddings - Index ready for RAG")