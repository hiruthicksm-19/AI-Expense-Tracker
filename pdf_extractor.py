"""
CLI Script for batch processing invoices.

Usage:
    python pdf_extractor.py
    
Processes all PDF files in the 'invoices/' directory and saves
extracted data to 'output/invoices.json' and MongoDB.
"""

from pathlib import Path

from config import INPUT_DIR, OUTPUT_DIR
from modules import (
    extract_pdf_text,
    InvoiceExtractor,
    InvoiceValidator,
    FileHandler,
)
from mongodb_handler import MongoDBHandler


def main():
    """Main CLI entry point for batch invoice processing."""
    
    # Ensure directories exist
    INPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Get all PDF files
    pdf_files = sorted(INPUT_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF invoices found in 'invoices/' directory.")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) to process.\n")
    
    # Initialize components
    extractor = InvoiceExtractor()
    validator = InvoiceValidator()
    invoices = []
    
    # Process each PDF
    for idx, pdf_path in enumerate(pdf_files, start=1):
        print(f"[{idx}/{len(pdf_files)}] Processing: {pdf_path.name}")
        
        try:
            # Extract text
            invoice_text = extract_pdf_text(pdf_path)
            
            if not invoice_text:
                print("Skipped: No extractable text found.\n")
                continue
            
            # Extract with LLM
            extracted_data = extractor.extract(invoice_text)
            
            # Validate
            invoice = validator.validate(extracted_data)
            invoices.append(invoice)
            
            print(f"Successfully extracted invoice #{invoice.get('invoice_number', 'Unknown')}\n")
        
        except Exception as error:
            print(f"Error: {error}\n")
    
    if not invoices:
        print("No invoices were successfully extracted.")
        return
    
    # Save to JSON
    print(f"Saving {len(invoices)} invoice(s) to JSON...")
    FileHandler.save_invoices_to_json(invoices)
    print("Saved to output/invoices.json\n")
    
    # Save to MongoDB
    print("Inserting into MongoDB with duplicate detection...")
    try:
        mongodb = MongoDBHandler()
        
        inserted_count = 0
        duplicate_count = 0
        
        for invoice in invoices:
            invoice_number = invoice.get("invoice_number")
            
            if mongodb.invoice_exists(invoice_number):
                print(f"WARNING: Duplicate - Invoice #{invoice_number} already in database")
                duplicate_count += 1
            else:
                mongodb.insert_invoice(invoice)
                inserted_count += 1
        
        mongodb.close()
        
        print(f"\nSuccessfully inserted {inserted_count} new invoice(s)")
        if duplicate_count > 0:
            print(f"Skipped {duplicate_count} duplicate(s)")
        
    except Exception as error:
        print(f"MongoDB Error: {error}")
    
    print("\nBatch processing complete!")


if __name__ == "__main__":
    main()
