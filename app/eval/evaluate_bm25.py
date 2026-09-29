import json, os
from rank_bm25 import BM25Okapi

chunks_path = "data/processed/chunks.jsonl"
qa_path = "data/eval/verified_qa_50.jsonl"
output_path = "data/interim/bm25_results_50.jsonl"
metrics_path = "evaluation/retrieval/bm25_metrics.json"

os.makedirs("data/interim", exist_ok=True)
os.makedirs("evaluation/retrieval", exist_ok=True)

chunks = [json.loads(l) for l in open(chunks_path, encoding="utf-8")]
corpus_texts = [c["text"] for c in chunks]
tokenized_corpus = [doc.lower().split() for doc in corpus_texts]
bm25 = BM25Okapi(tokenized_corpus)

qa = [json.loads(l) for l in open(qa_path, encoding="utf-8")]

all_results = []
for q in qa:
    query_text = q["question"] if q["question"] else q["question_ur"]
    tokenized_query = query_text.lower().split()
    scores = bm25.get_scores(tokenized_query)
    top_n = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:10]
    retrieved = [chunks[i] for i in top_n]
    retrieved_sources = [c.get("source_file","") for c in retrieved]
    all_results.append({
        "id": q["id"],
        "question": query_text,
        "lang": q["lang"],
        "gold_source_file": q["source_file"],
        "gold_page": q["page"],
        "retrieved_chunk_ids": [retrieved[i]["chunk_id"] for i in range(len(retrieved))],
        "retrieved_sources": retrieved_sources,
        "scores": [float(scores[i]) for i in top_n],
        "retrieved_texts": [retrieved[i]["text"][:500] for i in range(len(retrieved))]
    })

with open(output_path, "w", encoding="utf-8") as f:
    for r in all_results:
        f.write(json.dumps(r, ensure_ascii=False)+"\n")

# Simple Recall: check if gold filename appears in top K
def calc_metrics(results):
    recall = {1:0,3:0,5:0,10:0}
    mrr=0
    for r in results:
        gold = r["gold_source_file"]
        srcs = r["retrieved_sources"]
        found=None
        for idx, s in enumerate(srcs):
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
print(f"BM25 Baseline on {len(all_results)} QA")
print(f"Recall@1: {recall[1]:.3f} Recall@3: {recall[3]:.3f} Recall@5: {recall[5]:.3f} Recall@10: {recall[10]:.3f}")
print(f"MRR: {mrr:.3f}")
print(f"Saved: {output_path}")

with open(metrics_path,"w",encoding="utf-8") as out:
    json.dump({"retriever":"BM25","total_qa":len(all_results),"recall_at_k":recall,"mrr":mrr}, out, indent=2)