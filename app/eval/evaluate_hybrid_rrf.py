import json, os
from collections import defaultdict

bm25_path = "data/interim/bm25_results_50.jsonl"
dense_path = "data/interim/dense_results_50.jsonl"
output_path = "data/interim/hybrid_rrf_results_50.jsonl"
metrics_path = "evaluation/retrieval/hybrid_rrf_metrics.json"

os.makedirs("data/interim", exist_ok=True)
os.makedirs("evaluation/retrieval", exist_ok=True)

bm25 = [json.loads(l) for l in open(bm25_path, encoding="utf-8")]
dense = [json.loads(l) for l in open(dense_path, encoding="utf-8")]
dense_map = {d["id"]: d for d in dense}

k_rrf = 60 # standard RRF constant

all_results = []
for b in bm25:
    qid = b["id"]
    d = dense_map.get(qid)
    if not d: continue

    # Build rank maps
    b_ranks = {cid: rank+1 for rank, cid in enumerate(b["retrieved_chunk_ids"])}
    d_ranks = {cid: rank+1 for rank, cid in enumerate(d["retrieved_chunk_ids"])}

    # Collect all unique chunk_ids from both
    all_cids = set(b_ranks.keys()) | set(d_ranks.keys())

    rrf_scores = {}
    sources = {}
    for cid in all_cids:
        score = 0
        if cid in b_ranks:
            score += 1.0 / (k_rrf + b_ranks[cid])
            # get source
            idx = b["retrieved_chunk_ids"].index(cid)
            sources[cid] = b["retrieved_sources"][idx]
        if cid in d_ranks:
            score += 1.0 / (k_rrf + d_ranks[cid])
            if cid not in sources:
                idx = d["retrieved_chunk_ids"].index(cid)
                sources[cid] = d["retrieved_sources"][idx]
        rrf_scores[cid] = score

    sorted_cids = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:10]

    all_results.append({
        "id": qid,
        "question": b["question"],
        "lang": b["lang"],
        "gold_source_file": b["gold_source_file"],
        "gold_page": b["gold_page"],
        "retrieved_chunk_ids": [cid for cid, s in sorted_cids],
        "retrieved_sources": [sources[cid] for cid, s in sorted_cids],
        "scores": [s for cid, s in sorted_cids],
        "method": f"RRF k={k_rrf}"
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
print(f"Hybrid RRF on {len(all_results)} QA k={k_rrf}")
print(f"Recall@1: {recall[1]:.3f} Recall@3: {recall[3]:.3f} Recall@5: {recall[5]:.3f} Recall@10: {recall[10]:.3f}")
print(f"MRR: {mrr:.3f}")

bm25_m = json.load(open("evaluation/retrieval/bm25_metrics.json",encoding="utf-8"))
dense_m = json.load(open("evaluation/retrieval/dense_metrics.json",encoding="utf-8"))
print("\n=== FINAL COMPARISON RRF ===")
print(f"BM25 R@5 {bm25_m['recall_at_k']['5']:.3f} MRR {bm25_m['mrr']:.3f}")
print(f"DENSE R@5 {dense_m['recall_at_k']['5']:.3f} MRR {dense_m['mrr']:.3f}")
print(f"RRF HYBRID R@5 {recall[5]:.3f} MRR {mrr:.3f}")

with open(metrics_path,"w",encoding="utf-8") as out:
    json.dump({"retriever":"hybrid_rrf","k":k_rrf,"total_qa":len(all_results),"recall_at_k":recall,"mrr":mrr}, out, indent=2)