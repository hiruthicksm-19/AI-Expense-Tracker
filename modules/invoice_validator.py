"""
Module for validating and normalizing invoice data.
"""

from datetime import datetime
from config import INVOICE_FIELDS


class InvoiceValidator:
    """Validates and normalizes invoice data to match schema."""
    
    MONTH_NAMES = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }
    
    @staticmethod
    def validate(data: dict) -> dict:
        """
        Validate and normalize invoice data.
        
        Args:
            data: Raw extracted invoice data
            
        Returns:
            Validated and normalized invoice dictionary
            
        Raises:
            ValueError: If data structure is invalid
        """
        if not isinstance(data, dict):
            raise ValueError("Expected a JSON object.")
        
        # Initialize with all fields set to None
        invoice = {
            field: data.get(field)
            for field in INVOICE_FIELDS
        }
        
        # MongoDB generates _id automatically
        invoice["_id"] = None
        
        # Extract month and year from invoice_date
        invoice_date = invoice.get("invoice_date")
        
        # Process month - convert to name if it's a number, or extract from date
        month = invoice.get("month")
        if isinstance(month, int) and 1 <= month <= 12:
            # LLM provided month as number, convert to name
            invoice["month"] = InvoiceValidator.MONTH_NAMES.get(month)
        elif invoice_date:
            # Extract month from invoice_date if not provided or invalid
            try:
                parsed_date = datetime.strptime(invoice_date, "%Y-%m-%d")
                invoice["month"] = InvoiceValidator.MONTH_NAMES.get(parsed_date.month)
            except (ValueError, TypeError):
                invoice["month"] = None
        else:
            invoice["month"] = None
        
        # Process year - convert to string if it's a number, or extract from date
        year = invoice.get("year")
        if isinstance(year, int):
            # LLM provided year as number, convert to string
            invoice["year"] = str(year)
        elif invoice_date:
            # Extract year from invoice_date if not provided
            try:
                parsed_date = datetime.strptime(invoice_date, "%Y-%m-%d")
                invoice["year"] = str(parsed_date.year)
            except (ValueError, TypeError):
                invoice["year"] = None
        else:
            invoice["year"] = None
        
        # Normalize numeric fields
        for field in ("quantity", "total_amount"):
            value = invoice[field]
            
            if value is not None:
                try:
                    if isinstance(value, bool):
                        raise ValueError("Boolean is not a number")
                    
                    if isinstance(value, str):
                        value = value.replace(",", "").strip()
                    
                    invoice[field] = float(value)
                    
                    if field == "quantity":
                        number = invoice[field]
                        if number.is_integer():
                            invoice[field] = int(number)
                
                except (ValueError, TypeError):
                    invoice[field] = None
        
        # Ensure other fields are strings or null
        for field in INVOICE_FIELDS:
            if field in ("_id", "quantity", "total_amount", "month", "year"):
                continue
            
            value = invoice[field]
            
            if value is not None:
                if not isinstance(value, str):
                    invoice[field] = None
                else:
                    invoice[field] = value.strip() or None
        
        return invoice
