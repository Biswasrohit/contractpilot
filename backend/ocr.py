"""Google Vision OCR for scanned PDF documents.

Uses PyMuPDF to convert PDF pages to images, then Google Cloud Vision
document_text_detection to extract text with structure.
"""

import fitz  # pymupdf
from google.cloud import vision


def ocr_pdf(pdf_bytes: bytes) -> str:
    """Extract text from a scanned PDF using Google Cloud Vision OCR.

    Args:
        pdf_bytes: Raw PDF file bytes.

    Returns:
        Full extracted text with page breaks.
    """
    client = vision.ImageAnnotatorClient()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = []

    for page in doc:
        pix = page.get_pixmap(dpi=300)
        image = vision.Image(content=pix.tobytes("png"))
        response = client.document_text_detection(image=image)

        if response.error.message:
            raise RuntimeError(f"Vision API error: {response.error.message}")

        if response.full_text_annotation:
            full_text.append(response.full_text_annotation.text)

    doc.close()
    return "\n\n".join(full_text)
