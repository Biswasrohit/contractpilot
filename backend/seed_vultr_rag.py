"""One-time script: download legal datasets from Kaggle and upload to Vultr vector store.

Datasets:
  - CUAD: 500+ contracts, 41 clause types (expert-annotated)
  - Legal Clauses: 21K+ clauses, 16 types

Usage:
    python seed_vultr_rag.py
"""

import json
import os
import sys

import httpx
import kagglehub
from dotenv import load_dotenv

load_dotenv()

VULTR_BASE = "https://api.vultrinference.com/v1"
VULTR_API_KEY = os.environ.get("VULTR_INFERENCE_API_KEY", "")
COLLECTION_ID = os.environ.get("VULTR_LEGAL_COLLECTION_ID", "")
HEADERS = {
    "Authorization": f"Bearer {VULTR_API_KEY}",
    "Content-Type": "application/json",
}

# CUAD clause types for reference
CUAD_CLAUSE_TYPES = [
    "Non-Compete", "Non-Solicitation", "Non-Disparagement", "Termination",
    "Indemnification", "Limitation of Liability", "Intellectual Property",
    "Confidentiality", "Exclusivity", "Assignment", "Change of Control",
    "Anti-Assignment", "Revenue/Profit Sharing", "Price Restrictions",
    "Minimum Commitment", "Volume Restriction", "IP Ownership Assignment",
    "Joint IP Ownership", "License Grant", "Non-Transferable License",
    "Affiliate License", "Uncapped Liability", "Cap on Liability",
    "Liquidated Damages", "Warranty Duration", "Insurance",
    "Covenant Not to Sue", "Third Party Beneficiary", "Audit Rights",
    "Renewal", "Expiration Date", "Post-Termination Services",
    "Competitive Restriction Exception", "Rofr/Rofo/Rofn",
    "Most Favored Nation", "Governing Law", "Arbitration",
    "Irrevocable or Perpetual License", "Source Code Escrow",
    "Effective Date", "Subsequent Agreement",
]


def download_cuad() -> str:
    """Download CUAD dataset from Kaggle. Returns path to dataset."""
    print("Downloading CUAD dataset...")
    path = kagglehub.dataset_download("theatticusproject/atticus-open-contract-dataset-aok-beta")
    print(f"  Downloaded to: {path}")
    return path


def download_legal_clauses() -> str:
    """Download Legal Clauses dataset from Kaggle. Returns path to dataset."""
    print("Downloading Legal Clauses dataset...")
    path = kagglehub.dataset_download("mohammedalrashidan/contracts-clauses-datasets")
    print(f"  Downloaded to: {path}")
    return path


def process_cuad(dataset_path: str) -> list[dict]:
    """Process CUAD dataset into reference items for the vector store."""
    items = []

    # CUAD contains JSON annotations mapping clause types to contract text
    for root, _, files in os.walk(dataset_path):
        for fname in files:
            if not fname.endswith(".json"):
                continue

            fpath = os.path.join(root, fname)
            try:
                with open(fpath) as f:
                    data = json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue

            # Extract clause annotations
            if isinstance(data, dict) and "data" in data:
                for entry in data["data"][:50]:  # Limit per file
                    for para in entry.get("paragraphs", []):
                        context = para.get("context", "")[:2000]
                        for qa in para.get("qas", []):
                            clause_type = qa.get("question", "Unknown")
                            answers = qa.get("answers", [])
                            if answers:
                                clause_text = answers[0].get("text", "")
                                if len(clause_text) > 20:
                                    items.append({
                                        "content": (
                                            f"Clause Type: {clause_type}\n"
                                            f"Standard Language: {clause_text}\n"
                                            f"Source: CUAD Expert-Annotated Dataset\n"
                                            f"Context: {context[:500]}"
                                        ),
                                        "description": f"CUAD reference: {clause_type}",
                                    })

    print(f"  Processed {len(items)} CUAD reference items")
    return items


def process_legal_clauses(dataset_path: str) -> list[dict]:
    """Process Legal Clauses dataset into reference items."""
    items = []

    for root, _, files in os.walk(dataset_path):
        for fname in files:
            if not fname.endswith(".csv"):
                continue

            fpath = os.path.join(root, fname)
            try:
                import csv
                with open(fpath, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        clause_text = row.get("clause_text", row.get("text", ""))
                        clause_type = row.get("clause_type", row.get("type", "Unknown"))

                        if clause_text and len(clause_text) > 20:
                            items.append({
                                "content": (
                                    f"Clause Type: {clause_type}\n"
                                    f"Standard Language: {clause_text[:2000]}\n"
                                    f"Source: Legal Clauses Dataset"
                                ),
                                "description": f"Legal clause reference: {clause_type}",
                            })
            except Exception as e:
                print(f"  Warning: Could not process {fname}: {e}")

    print(f"  Processed {len(items)} Legal Clauses reference items")
    return items


def upload_to_vultr(items: list[dict], batch_size: int = 50) -> None:
    """Upload reference items to Vultr vector store."""
    if not VULTR_API_KEY or not COLLECTION_ID:
        print("ERROR: Set VULTR_INFERENCE_API_KEY and VULTR_LEGAL_COLLECTION_ID in .env")
        sys.exit(1)

    print(f"Uploading {len(items)} items to Vultr vector store...")

    with httpx.Client(timeout=60) as client:
        for i in range(0, len(items), batch_size):
            batch = items[i : i + batch_size]
            for item in batch:
                try:
                    response = client.post(
                        f"{VULTR_BASE}/vector_store/{COLLECTION_ID}/items",
                        headers=HEADERS,
                        json=item,
                    )
                    response.raise_for_status()
                except httpx.HTTPStatusError as e:
                    print(f"  Warning: Failed to upload item: {e}")

            uploaded = min(i + batch_size, len(items))
            print(f"  Uploaded {uploaded}/{len(items)}")

    print("Upload complete!")


def main():
    print("=== ContractPilot: Seeding Vultr Legal Knowledge Base ===\n")

    # Download datasets
    cuad_path = download_cuad()
    clauses_path = download_legal_clauses()

    # Process into reference items
    print("\nProcessing datasets...")
    cuad_items = process_cuad(cuad_path)
    clause_items = process_legal_clauses(clauses_path)

    all_items = cuad_items + clause_items
    print(f"\nTotal reference items: {len(all_items)}")

    if not all_items:
        print("WARNING: No items to upload. Check dataset paths.")
        return

    # Upload to Vultr
    print()
    upload_to_vultr(all_items)

    print("\n=== Done! Legal knowledge base is ready. ===")


if __name__ == "__main__":
    main()
