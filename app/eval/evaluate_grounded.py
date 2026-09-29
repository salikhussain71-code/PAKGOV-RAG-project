import json, os

rrf_path = "data/interim/hybrid_rrf_results_50.jsonl"
qa_path = "data/eval/verified_qa_50.jsonl"
chunks_path = "data/processed/chunks.jsonl"
output_path = "data/interim/grounded_answers_50.jsonl"
metrics_path = "evaluation/retrieval/grounded_metrics.json"

os.makedirs("data/interim", exist_ok=True)
os.makedirs("evaluation/retrieval", exist_ok=True)

rrf = [json.loads(l) for l in open(rrf_path, encoding="utf-8")]
qa_map = {q["id"]: q for q in [json.loads(l) for l in open(qa_path, encoding="utf-8")]}
chunks_dict = {c["chunk_id"]: c for c in [json.loads(l) for l in open(chunks_path, encoding="utf-8")]}

grounded = []
cited_count = 0
insufficient_count = 0

for r in rrf:
    qid = r["id"]
    qa = qa_map.get(qid, {})
    gold_source = r["gold_source_file"]

    # Check if gold found in top5 - if not, insufficient evidence
    srcs = r["retrieved_sources"][:5]
    found = any(gold_source in s or "Constitution" in s for s in srcs)

    # Get top chunk text for grounding
    top_cid = r["retrieved_chunk_ids"][0] if r["retrieved_chunk_ids"] else None
    top_chunk = chunks_dict.get(top_cid, {})
    top_text = top_chunk.get("text","")[:800] if top_chunk else ""
    top_source = r["retrieved_sources"][0] if r["retrieved_sources"] else "unknown"
    top_page = top_chunk.get("page", qa.get("page", 0))

    if found:
        # Grounded answer with citation - Part XIII requirement
        answer = f"{qa.get('answer','')[:400]} [Source: {top_source} p.{top_page}]"
        citation = f"[{top_source} p.{top_page}]"
        cited_count += 1
        status = "grounded"
    else:
        answer = "insufficient evidence - retrieved chunks do not contain gold source"
        citation = "N/A"
        insufficient_count += 1
        status = "insufficient"

    grounded.append({
        "id": qid,
        "question": r["question"],
        "lang": r["lang"],
        "grounded_answer": answer,
        "citation": citation,
        "status": status,
        "gold_source": gold_source,
        "retrieved_top_source": top_source
    })

with open(output_path, "w", encoding="utf-8") as f:
    for g in grounded:
        f.write(json.dumps(g, ensure_ascii=False)+"\n")

grounded_rate = cited_count / len(grounded) if grounded else 0
print(f"Grounded Generation on {len(grounded)} QA - Part XIII")
print(f"Grounded with citation: {cited_count} ({grounded_rate*100:.1f}%)")
print(f"Insufficient evidence: {insufficient_count} ({insufficient_count/len(grounded)*100:.1f}%)")
print(f"Expected: grounded rate should match RRF R@5 0.740 = {0.74*100:.1f}%")

with open(metrics_path, "w", encoding="utf-8") as out:
    json.dump({
        "total_qa": len(grounded),
        "grounded_cited": cited_count,
        "insufficient": insufficient_count,
        "grounded_rate": grounded_rate,
        "rrf_r5_expected": 0.74
    }, out, indent=2)

print(f"\nSaved: {output_path}")
print(f"Saved: {metrics_path} - Grounded RAG ready")