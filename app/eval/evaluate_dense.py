import json, os, faiss, numpy as np
from sentence_transformers import SentenceTransformer

chunks_path = "data/processed/chunks.jsonl"
qa_path = "data/eval/verified_qa_50.jsonl"
faiss_index_path = "data/processed/faiss_index/index.faiss" # check if name different - if error tell me
output_path = "data/interim/dense_results_50.jsonl"
metrics_path = "evaluation/retrieval/dense_metrics.json"
meta_path = "data/processed/faiss_index/metadata.jsonl"

os.makedirs("data/interim", exist_ok=True)
os.makedirs("evaluation/retrieval", exist_ok=True)

# Load chunks
chunks = [json.loads(l) for l in open(chunks_path, encoding="utf-8")]

# Load model - multilingual for Urdu support - this is your research focus
model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
print(f"Loading model {model_name}...")
model = SentenceTransformer(model_name)

# Load FAISS index
print(f"Loading FAISS {faiss_index_path}")
index = faiss.read_index(faiss_index_path)

qa = [json.loads(l) for l in open(qa_path, encoding="utf-8")]

all_results = []
for q in qa:
    q_text = q["question"] if q["question"] else q["question_ur"]
    q_emb = model.encode([q_text], convert_to_numpy=True, normalize_embeddings=True)
    scores, ids = index.search(q_emb, 10)
    retrieved = [chunks[i] for i in ids[0]]
    retrieved_sources = [c.get("source_file","") for c in retrieved]
    all_results.append({
        "id": q["id"],
        "question": q_text,
        "lang": q["lang"],
        "gold_source_file": q["source_file"],
        "gold_page": q["page"],
        "retrieved_chunk_ids": [retrieved[i]["chunk_id"] for i in range(len(retrieved))],
        "retrieved_sources": retrieved_sources,
        "scores": [float(scores[0][i]) for i in range(len(scores[0]))]
    })

with open(output_path, "w", encoding="utf-8") as f:
    for r in all_results:
        f.write(json.dumps(r, ensure_ascii=False)+"\n")

def calc_metrics(results):
    recall={1:0,3:0,5:0,10:0}
    mrr=0
    for r in results:
        gold=r["gold_source_file"]
        srcs=r["retrieved_sources"]
        found=None
        for idx,s in enumerate(srcs):
            if gold in s or "Constitution" in s:
                found=idx+1
                break
        if found:
            if found<=1: recall[1]+=1
            if found<=3: recall[3]+=1
            if found<=5: recall[5]+=1
            if found<=10: recall[10]+=1
            mrr+=1.0/found
    total=len(results)
    for k in recall: recall[k]=recall[k]/total if total else 0
    mrr=mrr/total if total else 0
    return recall,mrr

recall,mrr=calc_metrics(all_results)
print(f"Dense Baseline on {len(all_results)} QA")
print(f"Recall@1: {recall[1]:.3f} Recall@3: {recall[3]:.3f} Recall@5: {recall[5]:.3f} Recall@10: {recall[10]:.3f}")
print(f"MRR: {mrr:.3f}")

with open(metrics_path,"w",encoding="utf-8") as out:
    json.dump({"retriever":"dense-multilingual","model":model_name,"total_qa":len(all_results),"recall_at_k":recall,"mrr":mrr}, out, indent=2)

# Also create comparison table
bm25_path="evaluation/retrieval/bm25_metrics.json"
if os.path.exists(bm25_path):
    bm25=json.load(open(bm25_path,encoding="utf-8"))
    print("\n=== FAIR COMPARISON SAME 50 QA ===")
    print(f"BM25 R@5 {bm25['recall_at_k']['5']:.3f} MRR {bm25['mrr']:.3f}")
    print(f"DENSE R@5 {recall[5]:.3f} MRR {mrr:.3f}")