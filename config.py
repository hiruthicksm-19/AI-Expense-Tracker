"""
Configuration settings for the Invoice Extractor application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================
# Directory Configuration
# ============================================================

BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "invoices"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_FILE = OUTPUT_DIR / "invoices.json"

# ============================================================
# API Configuration
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is missing. Add it to your .env file."
    )

MODEL_NAME = "openai/gpt-oss-120b"

# ============================================================
# MongoDB Configuration
# ============================================================

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb://localhost:27017"
)

MONGODB_DATABASE = os.getenv(
    "MONGODB_DATABASE",
    "invoice_tracker"
)

MONGODB_COLLECTION = os.getenv(
    "MONGODB_COLLECTION",
    "invoices"
)

# ============================================================
# Invoice Schema Fields
# ============================================================

INVOICE_FIELDS = [
    "_id",
    "invoice_number",
    "invoice_date",
    "month",
    "year",
    "seller_name",
    "seller_address",
    "description",
    "quantity",
    "total_amount",
    "payment_details",
]

# ============================================================
# LLM System Prompt
# ============================================================

SYSTEM_PROMPT = """
You are an expert invoice information extraction assistant.

Your task is to analyze raw text extracted from PDF invoices
and convert it into a structured JSON object.

Return ONLY valid JSON with the following structure:

{
    "_id": null,
    "invoice_number": null,
    "invoice_date": null,
    "month": null,
    "year": null,
    "seller_name": null,
    "seller_address": null,
    "description": null,
    "quantity": null,
    "total_amount": null,
    "payment_details": null
}

Extraction rules:

1. Extract information ONLY from the supplied invoice text.
2. Never invent or assume missing information.
3. If a field cannot be determined, return null.
4. invoice_number: Extract the invoice identifier, not the order number.
5. invoice_date: Return the date in YYYY-MM-DD format.
6. month: Extract the month from invoice_date as a number (1-12), or null if date is unavailable.
7. year: Extract the year from invoice_date as a number (YYYY), or null if date is unavailable.
8. seller_name: Extract the supplier or seller, not the buyer.
9. seller_address: Extract the complete seller address.
10. description: Extract the product or service description.
    If multiple items exist, combine their descriptions into
    one string separated by semicolons.
11. quantity: Extract the total quantity of products or services.
12. total_amount: Extract the final invoice amount as a number.
13. payment_details: Extract the payment method or payment information.
14. Return valid JSON only, with no markdown or explanation.
"""
