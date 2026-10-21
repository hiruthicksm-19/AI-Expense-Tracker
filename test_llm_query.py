#!/usr/bin/env python
"""Test the LLM-powered query pipeline."""

from mongodb_handler import MongoDBHandler
from modules import LLMQueryPipeline

print("\n=== LLM Query Pipeline Test ===\n")

try:
    # Connect to MongoDB
    print("Connecting to MongoDB...")
    mongodb = MongoDBHandler()
    
    # Initialize pipeline
    print("Initializing LLM Query Pipeline...")
    pipeline = LLMQueryPipeline(mongodb.collection)
    
    # Get schema
    schema = pipeline.get_collection_schema()
    print(f"Schema fields: {schema.get('fields', [])}")
    print(f"Total documents: {schema.get('total_documents', 0)}\n")
    
    # Test questions
    test_questions = [
        "What is the total amount spent?",
        "How many invoices?",
        "Show top 2 invoices by amount",
    ]
    
    for question in test_questions:
        print(f"Question: {question}")
        print("-" * 70)
        
        answer, metadata = pipeline.process_question(question)
        
        print(f"Answer: {answer}")
        print(f"Results found: {metadata.get('result_count', 0)}")
        
        if metadata.get('pipeline'):
            print(f"Generated Pipeline: {metadata['pipeline']}")
        
        if metadata.get('error'):
            print(f"Error: {metadata['error']}")
        
        print()
    
    mongodb.close()
    print("Test completed successfully!")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
