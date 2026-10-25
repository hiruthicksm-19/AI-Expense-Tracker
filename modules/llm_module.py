"""
Module for LLM-based invoice data extraction using Groq.
"""

import json
import os
import certifi
from groq import Groq

from config import GROQ_API_KEY, MODEL_NAME, SYSTEM_PROMPT


class InvoiceExtractor:
    """Handles invoice extraction using Groq LLM."""
    
    def __init__(self):
        """Initialize the Groq client."""
        # Set SSL certificate for Groq API
        os.environ['SSL_CERT_FILE'] = certifi.where()
        
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = MODEL_NAME
        self.system_prompt = SYSTEM_PROMPT
    
    def extract(self, invoice_text: str) -> dict:
        """
        Extract invoice data from text using Groq LLM.
        
        Args:
            invoice_text: Raw text extracted from PDF
            
        Returns:
            Extracted invoice data as dictionary
            
        Raises:
            ValueError: If LLM response is invalid
            Exception: If Groq API call fails
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": (
                            "Extract invoice information from "
                            "the following PDF text:\n\n"
                            + invoice_text
                        )
                    }
                ]
            )
            
            if response.choices[0].finish_reason != "stop":
                raise ValueError("LLM response was incomplete.")
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Groq returned an empty response.")
            
            return json.loads(content)
        
        except Exception as e:
            raise Exception(f"Error processing with LLM: {str(e)}")
