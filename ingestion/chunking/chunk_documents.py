import json
from pathlib import Path
def chunk_text(text, chunk_size=1000, overlap=200):
    chunks=[]; start=0
    while start < len(text):
        end=min(start+chunk_size, len(text))
        chunks.append(text[start:end])
        start+=chunk_size-overlap
    return chunks
def run(input_file, output_file):
    input_file=Path(input_file); output_file=Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True); total=0
    with open(input_file,'r',encoding='utf-8') as f, open(output_file,'w',encoding='utf-8') as out:
        for line in f:
            if not line.strip(): continue
            rec=json.loads(line); txt=rec['text']
            for ch in chunk_text(txt):
                out.write(json.dumps({"text": ch, "source_file": rec['source_file']}, ensure_ascii=False)+"\n")
                total+=1
    print(f"Saved {total} chunks to {output_file}")
if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    run(a.input, a.output)