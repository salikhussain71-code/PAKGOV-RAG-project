import fitz, json
from pathlib import Path
def extract_pdfs(input_dir, output_file):
    input_dir=Path(input_dir); output_file=Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    count=0
    with open(output_file,'w',encoding='utf-8') as out:
        for pdf in input_dir.glob("*.pdf"):
            doc=fitz.open(str(pdf))
            text=""
            for page in doc:
                text+=page.get_text()
            record={"source_file": pdf.name, "text": text, "pages": len(doc)}
            out.write(json.dumps(record, ensure_ascii=False)+"\n")
            count+=1
            print(f"Extracted {pdf.name} - {len(doc)} pages - {len(text)} chars")
    print(f"Total {count} PDFs saved to {output_file}")
if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    extract_pdfs(args.input, args.output)