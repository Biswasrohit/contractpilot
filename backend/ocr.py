"""Tesseract OCR for scanned PDF documents.

Uses PyMuPDF to convert PDF pages to images, then pytesseract
for local OCR text extraction. No cloud API or credentials required.
"""

import concurrent.futures
import io

import fitz  # pymupdf
import pytesseract
from PIL import Image


def _ocr_single_page(page_bytes: bytes) -> str:
    """OCR a single page image using Tesseract."""
    image = Image.open(io.BytesIO(page_bytes))
    text = pytesseract.image_to_string(image, lang="eng")
    return text.strip()


def ocr_pdf(pdf_bytes: bytes) -> str:
    """Extract text from a scanned PDF using Tesseract OCR.

    Args:
        pdf_bytes: Raw PDF file bytes.

    Returns:
        Full extracted text with page breaks.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    # Convert all pages to PNG at 200 DPI
    page_images = []
    for page in doc:
        pix = page.get_pixmap(dpi=200)
        page_images.append(pix.tobytes("png"))
    doc.close()

    # Process pages concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(_ocr_single_page, img) for img in page_images]
        results = [f.result(timeout=60) for f in futures]

    return "\n\n".join(results)
