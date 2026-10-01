import fitz
from pathlib import Path

def ocr_pdf(pdf_path):
    pdf_path = Path(pdf_path)
    try:
        import pytesseract
        from PIL import Image
        HAS_TESS = True
    except:
        HAS_TESS = False
        return f"[SCANNED PDF - {pdf_path.name} - OCR requires Tesseract install from https://github.com/UB-Mannheim/tesseract/wiki - Placeholder]"

    doc = fitz.open(str(pdf_path))
    full_text = ""
    for page in doc:
        t = page.get_text()
        if len(t.strip()) > 100:
            full_text += t + "\n"
        else:
            if HAS_TESS:
                try:
                    pix = page.get_pixmap(dpi=300)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    ocr_text = pytesseract.image_to_string(img, lang='eng')
                    full_text += ocr_text + "\n"
                except Exception as e:
                    # Tesseract not installed on Windows
                    full_text += f"\n[SCANNED PAGE {page.number} in {pdf_path.name} - Install Tesseract OCR to extract - Skipped]\n"
            else:
                full_text += f"\n[SCANNED PAGE {page.number}]\n"
    return full_text