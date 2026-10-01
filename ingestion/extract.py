import fitz, json
from pathlib import Path

def extract_pdfs(input_dir, output_file):
    input_dir=Path(input_dir); output_file=Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    count=0; scanned=0
    try:
        from ocr.run_ocr import ocr_pdf
        HAS_OCR=True
    except:
        HAS_OCR=False
        def ocr_pdf(p): return "[SCANNED - OCR module missing]"

    with open(output_file,'w',encoding='utf-8') as out:
        for pdf in sorted(input_dir.glob("*.pdf")):
            doc=fitz.open(str(pdf))
            text=""
            for page in doc:
                text+=page.get_text()
            chars=len(text)
            if chars<100:
                scanned+=1
                print(f"0 chars detected {pdf.name} - {len(doc)} pages - SCANNED image PDF - marking for OCR later")
                # Don't crash - save placeholder + try OCR safe
                try:
                    ocr_text=ocr_pdf(pdf)
                    if len(ocr_text.strip())>100 and "SCANNED" not in ocr_text[:50]:
                        text=ocr_text
                        print(f"  -> OCR recovered {len(text)} chars")
                    else:
                        # Keep placeholder, don't crash
                        text=f"[SCANNED PDF {pdf.name} - {len(doc)} pages - Content requires OCR - Install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki - Placeholder for pipeline continuity]\n"
                except Exception as e:
                    text=f"[SCANNED PDF {pdf.name} - OCR failed {e} - Placeholder]\n"
                    print(f"  -> OCR failed, placeholder saved")
            record={"source_file": pdf.name, "text": text, "pages": len(doc), "chars": len(text)}
            out.write(json.dumps(record, ensure_ascii=False)+"\n")
            count+=1
            print(f"Extracted {pdf.name} - {len(doc)} pages - {len(text)} chars")
    print(f"Total {count} PDFs saved to {output_file} - {scanned} scanned PDFs handled without crash")

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    extract_pdfs(args.input, args.output)