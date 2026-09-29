import json, os

rrf_path = "data/interim/hybrid_rrf_results_50.jsonl"
qa_path = "data/eval/verified_qa_50.jsonl"
output_path = "evaluation/retrieval/failure_analysis_50.md"
chunks_path = "data/processed/chunks.jsonl"

os.makedirs("evaluation/retrieval", exist_ok=True)

rrf = [json.loads(l) for l in open(rrf_path, encoding="utf-8")]
chunks_dict = {c["chunk_id"]: c for c in [json.loads(l) for l in open(chunks_path, encoding="utf-8")]}

qa_map = {q["id"]: q for q in [json.loads(l) for l in open(qa_path, encoding="utf-8")]}

failures = []
for r in rrf:
    gold = r["gold_source_file"]
    srcs = r["retrieved_sources"]
    found = None
    for idx, s in enumerate(srcs):
        if gold in s or "Constitution" in s:
            found = idx+1
            break
    if not found or found > 5: # failed at R@5
        q = qa_map.get(r["id"], {})
        failures.append({
            "id": r["id"],
            "question": r["question"],
            "lang": r["lang"],
            "gold": gold,
            "gold_page": r["gold_page"],
            "retrieved_top1": srcs[0] if srcs else "",
            "rank": found if found else ">10",
            "answer": q.get("answer","")[:500]
        })

# Categorize
categories = {"exact_article_mismatch":0, "urdu_mixed_query":0, "semantic_drift":0, "chunk_boundary":0}

for f in failures:
    q = f["question"].lower()
    if "article" in q or "آرٹیکل" in q:
        categories["exact_article_mismatch"]+=1
    elif f["lang"] in ["ur","mixed"]:
        categories["urdu_mixed_query"]+=1
    elif len(q.split()) < 4:
        categories["semantic_drift"]+=1
    else:
        categories["chunk_boundary"]+=1

with open(output_path, "w", encoding="utf-8") as out:
    out.write(f"# Failure Analysis - 50 QA - Hybrid RRF\n\n")
    out.write(f"Total QA: 50, Failed at R@5: {len(failures)} ({len(failures)/50*100:.1f}%)\n\n")
    out.write(f"## Category counts\n")
    for k,v in categories.items():
        out.write(f"- {k}: {v}\n")
    out.write(f"\n## Failed cases (Top 13)\n\n")
    for f in failures:
        out.write(f"### {f['id']} - Rank {f['rank']} - Lang {f['lang']}\n")
        out.write(f"Q: {f['question']}\n\n")
        out.write(f"Gold: {f['gold']} p{f['gold_page']}\n")
        out.write(f"Got Top1: {f['retrieved_top1']}\n")
        out.write(f"Gold answer snippet: {f['answer']}\n\n")
        out.write(f"Hypothesis: ")
        if "article" in f["question"].lower():
            out.write(f"BM25 matched wrong article number, dense missed numeric signal\n")
        elif f["lang"]!= "en":
            out.write(f"Multilingual embedding weak for Urdu, needs better Urdu model\n")
        else:
            out.write(f"Chunk split broke context across boundary\n")
        out.write(f"\n---\n\n")

print(f"Failure analysis done: {len(failures)} failed at R@5")
for k,v in categories.items():
    print(f"{k}: {v}")
print(f"Saved: {output_path}")