import json, os
from collections import defaultdict

bm25_path = "data/interim/bm25_results_50.jsonl"
dense_path = "data/interim/dense_results_50.jsonl"
output_path = "data/interim/hybrid_results_50.jsonl"
metrics_path = "evaluation/retrieval/hybrid_metrics.json"

os.makedirs("data/interim", exist_ok=True)
os.makedirs("evaluation/retrieval", exist_ok=True)

bm25 = [json.loads(l) for l in open(bm25_path, encoding="utf-8")]
dense = [json.loads(l) for l in open(dense_path, encoding="utf-8")]

# Map dense scores by id for lookup
dense_map = {d["id"]: d for d in dense}

# Weight: alpha = 0.5 dense + 0.5 bm25 normalized
alpha = 0.6 # give more to dense for Urdu focus

all_results = []
for b in bm25:
    qid = b["id"]
    d = dense_map.get(qid)
    if not d:
        continue

    # Normalize scores to 0-1 per query
    b_scores = b["scores"]
    d_scores = d["scores"]
    b_min, b_max = min(b_scores), max(b_scores)
    d_min, d_max = min(d_scores), max(d_scores)
    b_norm = [(s-b_min)/(b_max-b_min+1e-9) for s in b_scores]
    d_norm = [(s-d_min)/(d_max-d_min+1e-9) for s in d_scores]

    # Combine by chunk_id
    combined = defaultdict(float)
    combined_sources = {}
    for i, cid in enumerate(b["retrieved_chunk_ids"]):
        combined[cid] += (1-alpha)*b_norm[i]
        combined_sources[cid] = b["retrieved_sources"][i] if i < len(b["retrieved_sources"]) else ""
    for i, cid in enumerate(d["retrieved_chunk_ids"]):
        combined[cid] += alpha*d_norm[i]
        if cid not in combined_sources:
            combined_sources[cid] = d["retrieved_sources"][i] if i < len(d["retrieved_sources"]) else ""

    # Sort by combined score top 10
    sorted_cids = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:10]

    all_results.append({
        "id": qid,
        "question": b["question"],
        "lang": b["lang"],
        "gold_source_file": b["gold_source_file"],
        "gold_page": b["gold_page"],
        "retrieved_chunk_ids": [cid for cid, score in sorted_cids],
        "retrieved_sources": [combined_sources[cid] for cid, score in sorted_cids],
        "scores": [score for cid, score in sorted_cids],
        "alpha": alpha
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

recall,mrr = calc_metrics(all_results)
print(f"Hybrid Baseline on {len(all_results)} QA alpha={alpha}")
print(f"Recall@1: {recall[1]:.3f} Recall@3: {recall[3]:.3f} Recall@5: {recall[5]:.3f} Recall@10: {recall[10]:.3f}")
print(f"MRR: {mrr:.3f}")

# Load old for comparison
import json as js
bm25_m = js.load(open("evaluation/retrieval/bm25_metrics.json",encoding="utf-8"))
dense_m = js.load(open("evaluation/retrieval/dense_metrics.json",encoding="utf-8"))
print("\n=== FINAL COMPARISON SAME 50 QA ===")
print(f"BM25 R@5 {bm25_m['recall_at_k']['5']:.3f} MRR {bm25_m['mrr']:.3f}")
print(f"DENSE R@5 {dense_m['recall_at_k']['5']:.3f} MRR {dense_m['mrr']:.3f}")
print(f"HYBRID R@5 {recall[5]:.3f} MRR {mrr:.3f}")

with open(metrics_path,"w",encoding="utf-8") as out:
    js.dump({"retriever":"hybrid","alpha":alpha,"total_qa":len(all_results),"recall_at_k":recall,"mrr":mrr}, out, indent=2)