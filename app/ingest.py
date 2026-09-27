import pymupdf
import glob
import os
import hashlib
from pathlib import Path

raw_dir = Path("data/raw")
files = list(raw_dir.glob("*.pdf"))

print(f"Found {len(files)} PDFs")

for f in files:
    doc = pymupdf.open(f)
    pages = len(doc)
    sha = hashlib.sha256(f.read_bytes()).hexdigest()[:8]
    print(f"{f.name} - {pages} pages - {sha}")