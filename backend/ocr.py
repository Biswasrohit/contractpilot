"""Google Vision OCR for scanned PDF documents.

Uses PyMuPDF to convert PDF pages to images, then Google Cloud Vision
document_text_detection to extract text with structure.

Optimized: 200 DPI (vs 300), concurrent page processing via thread pool.
"""

import concurrent.futures

import fitz  # pymupdf
from google.cloud import vision


def _ocr_single_page(client: vision.ImageAnnotatorClient, page_bytes: bytes) -> str:
    """OCR a single page image (sync, designed to run in thread pool)."""
    image = vision.Image(content=page_bytes)
    response = client.document_text_detection(image=image)

    if response.error.message:
        raise RuntimeError(f"Vision API error: {response.error.message}")

    if response.full_text_annotation:
        return response.full_text_annotation.text
    return ""


def ocr_pdf(pdf_bytes: bytes) -> str:
    """Extract text from a scanned PDF using Google Cloud Vision OCR.

    Args:
        pdf_bytes: Raw PDF file bytes.

    Returns:
        Full extracted text with page breaks.
    """
    client = vision.ImageAnnotatorClient()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    # Convert all pages to PNG at 200 DPI (was 300 — 2.25x less data, still readable)
    page_images = []
    for page in doc:
        pix = page.get_pixmap(dpi=200)
        page_images.append(pix.tobytes("png"))
    doc.close()

    # Process pages concurrently (Vision SDK is sync, so use threads)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = [
            pool.submit(_ocr_single_page, client, img)
            for img in page_images
        ]
        results = [f.result(timeout=30) for f in futures]

    return "\n\n".join(results)
