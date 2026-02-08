import asyncio
import os
from pathlib import Path

import fitz  # pymupdf
from convex import ConvexClient
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from agent import run_contract_analysis
from report_generator import generate_pdf_report

# Load .env from the backend directory regardless of cwd
load_dotenv(Path(__file__).parent / ".env")

app = FastAPI(title="ContractPilot Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Convex client for creating reviews and fetching results
convex = ConvexClient(os.environ.get("CONVEX_URL", ""))


def extract_text(file_bytes: bytes, filename: str, use_ocr: bool) -> tuple[str, bool]:
    """Extract text from a PDF or DOCX file. Returns (text, ocr_used).

    For PDFs: uses PyMuPDF direct extraction, or Tesseract OCR if use_ocr is True.
    For DOCX: uses python-docx (OCR is never needed).
    """
    if filename.lower().endswith(".docx"):
        from docx_extractor import extract_docx_text

        return extract_docx_text(file_bytes), False

    # PDF path — use Tesseract if user toggled OCR on
    if use_ocr:
        from ocr import ocr_pdf

        return ocr_pdf(file_bytes), True

    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    return text, False


async def _run_analysis(review_id: str, pdf_text: str, user_id: str, ocr_used: bool):
    """Background task: run the full agent analysis pipeline."""
    try:
        await run_contract_analysis(review_id, pdf_text, user_id, ocr_used)
    except Exception as e:
        import traceback
        print(f"Analysis failed for {review_id}: {e}")
        traceback.print_exc()
        try:
            convex.mutation("reviews:updateStatus", {"id": review_id, "status": "failed"})
        except Exception:
            pass


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze_contract(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Form("dev-user"),
    use_ocr: str = Form("false"),
):
    """Upload a contract (PDF or DOCX) and start AI analysis."""
    try:
        filename = file.filename or "document"
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in ("pdf", "docx"):
            from fastapi.responses import JSONResponse

            return JSONResponse(
                {"error": "Unsupported file type. Upload a PDF or Word (.docx) file."},
                status_code=400,
            )

        file_bytes = await file.read()
        print(f"Received file: {filename}, size: {len(file_bytes)} bytes")

        # Extract text (OCR only applies to PDFs when toggled on by user)
        ocr_flag = use_ocr.lower() in ("true", "1", "yes")
        doc_text, ocr_used = extract_text(file_bytes, filename, ocr_flag)
        print(f"Extracted {len(doc_text)} chars, ocr_used={ocr_used}")

        # Create review in Convex
        try:
            review_id = convex.mutation(
                "reviews:create",
                {"userId": user_id, "filename": filename},
            )
        except Exception:
            # Convex not configured — return placeholder
            return {"review_id": "demo", "status": "pending", "ocr_used": ocr_used}

        # Run analysis in background
        background_tasks.add_task(_run_analysis, review_id, doc_text, user_id, ocr_used)

        return {"review_id": review_id, "status": "pending", "ocr_used": ocr_used}
    except Exception as e:
        import traceback
        traceback.print_exc()
        from fastapi.responses import JSONResponse

        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/report/{review_id}")
async def get_report(review_id: str):
    """Download the PDF risk analysis report."""
    try:
        review = convex.query("reviews:get", {"id": review_id})
        clauses = convex.query("clauses:getByReview", {"reviewId": review_id})
    except Exception:
        return Response(content=b"Report not available", status_code=404)

    if not review or review.get("status") != "completed":
        return Response(content=b"Review not completed yet", status_code=202)

    pdf_bytes = generate_pdf_report(review, clauses or [])
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=contractpilot-report.pdf"},
    )
