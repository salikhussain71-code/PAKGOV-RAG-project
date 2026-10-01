import json, os
from pathlib import Path
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import argparse

def embed_chunks(input_file, output_dir):
    input_file=Path(input_file); output_dir=Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    chunks=[]
    with open(input_file,'r',encoding='utf-8') as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))
    texts=[c['text'] for c in chunks]
    print(f"Loading model paraphrase-multilingual-MiniLM-L12-v2 for {len(texts)} chunks...")
    model=SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    embeddings=model.encode(texts, show_progress_bar=True, batch_size=32)
    dim=embeddings.shape[1]
    index=faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings, dtype='float32'))
    faiss.write_index(index, str(output_dir / "index.faiss"))
    with open(output_dir / "chunks.jsonl",'w',encoding='utf-8') as out:
        for c in chunks:
            out.write(json.dumps(c, ensure_ascii=False)+"\n")
    print(f"Saved FAISS index with {index.ntotal} vectors to {output_dir}")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    embed_chunks(args.input, args.output)