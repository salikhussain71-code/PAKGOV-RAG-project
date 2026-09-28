import pathlib, json
interim_dir = pathlib.Path("data/interim")
processed_dir = pathlib.Path("data/processed")
processed_dir.mkdir(parents=True, exist_ok=True)
CHUNK_SIZE = 1000
OVERLAP = 200
out_path = processed_dir / "chunks.jsonl"
count = 0
with out_path.open("w", encoding="utf-8") as out:
    for txt_file in sorted(interim_dir.glob("*.txt")):
        text = txt_file.read_text(encoding="utf-8")
        start = 0
        chunk_id = 0
        while start < len(text):
            end = min(start + CHUNK_SIZE, len(text))
            chunk_text = text[start:end]
            if len(chunk_text.strip()) < 50:
                start += CHUNK_SIZE - OVERLAP
                continue
            record = {"source_file": txt_file.name, "chunk_id": f"{txt_file.stem}_{chunk_id}", "start_char": start, "end_char": end, "text": chunk_text}
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
            chunk_id += 1
            if end == len(text):
                break
            start += CHUNK_SIZE - OVERLAP
print(f"Done - {count} chunks written to {out_path}")