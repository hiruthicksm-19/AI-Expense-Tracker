"""
Module for extracting text from PDF files.
"""

import os
import tempfile
from pathlib import Path

import pymupdf as fitz


def extract_pdf_text(pdf_path: Path | str) -> str:
    """
    Extract all text from a PDF file using PyMuPDF.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text from all pages
        
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        Exception: If PDF extraction fails
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    try:
        text_parts = []
        
        with fitz.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf, start=1):
                text = page.get_text("text", sort=True).strip()
                if text:
                    text_parts.append(f"\n--- PAGE {page_num} ---\n{text}")
        
        return "\n".join(text_parts).strip()
    
    except Exception as e:
        raise Exception(f"Error extracting PDF text from {pdf_path}: {str(e)}")


def extract_pdf_text_from_upload(uploaded_file) -> str:
    """
    Extract text from an uploaded PDF file (for Streamlit).
    Used for handling file uploads in the web interface.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        Extracted text from the PDF
        
    Raises:
        Exception: If extraction fails
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name
        
        text = extract_pdf_text(tmp_path)
        os.unlink(tmp_path)
        
        return text
    
    except Exception as e:
        raise Exception(f"Error extracting uploaded PDF: {str(e)}")
