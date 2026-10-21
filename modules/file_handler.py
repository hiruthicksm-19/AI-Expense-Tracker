"""
Module for handling file operations (JSON export/import).
"""

import json
from pathlib import Path
from typing import List

from config import OUTPUT_DIR, OUTPUT_FILE


class FileHandler:
    """Handles file I/O operations for invoices."""
    
    @staticmethod
    def ensure_output_dir():
        """Create output directory if it doesn't exist."""
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def save_invoices_to_json(invoices: List[dict]) -> Path:
        """
        Save invoices to JSON file.
        
        Args:
            invoices: List of invoice dictionaries
            
        Returns:
            Path to the saved JSON file
        """
        FileHandler.ensure_output_dir()
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            json.dump(
                invoices,
                file,
                indent=2,
                ensure_ascii=False
            )
        
        return OUTPUT_FILE
    
    @staticmethod
    def load_invoices_from_json() -> List[dict]:
        """
        Load invoices from JSON file.
        
        Returns:
            List of invoices, empty list if file doesn't exist
        """
        if not OUTPUT_FILE.exists():
            return []
        
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, IOError):
            return []
    
    @staticmethod
    def export_to_json_string(invoices: List[dict]) -> str:
        """
        Export invoices as JSON string (for download).
        
        Args:
            invoices: List of invoice dictionaries
            
        Returns:
            JSON string representation
        """
        return json.dumps(invoices, indent=2, ensure_ascii=False)
