import pathlib, glob
import pymupdf

raw_dir = pathlib.Path("data/raw")
interim_dir = pathlib.Path("data/interim")
interim_dir.mkdir(parents=True, exist_ok=True)

for pdf_path in raw_dir.glob("*.pdf"):
    doc = pymupdf.open(pdf_path)
    text = "\n".join([page.get_text() for page in doc])
    out_path = interim_dir / f"{pdf_path.stem}.txt"
    out_path.write_text(text, encoding="utf-8")
    print(f"{pdf_path.name} -> {out_path.name} - {len(doc)} pages - {len(text)} chars")

print(f"Done - {len(list(interim_dir.glob('*.txt')))} txt files in {interim_dir}")