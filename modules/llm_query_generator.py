"""
Module for using LLM to generate MongoDB queries from natural language.

Workflow:
1. User asks question in natural language
2. LLM analyzes question and generates MongoDB aggregation pipeline
3. Pipeline executes against MongoDB
4. Results formatted for LLM
5. LLM generates human-readable answer
"""

import json
import os
import certifi
from typing import Dict, Any, List, Tuple
from groq import Groq
from config import GROQ_API_KEY, MODEL_NAME


class LLMQueryGenerator:
    """
    Uses Groq LLM to generate MongoDB queries from natural language questions.
    """
    
    def __init__(self):
        """Initialize the LLM client."""
        # Set SSL certificate for Groq API
        os.environ['SSL_CERT_FILE'] = certifi.where()
        
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = MODEL_NAME
    
    def generate_mongodb_query(self, question: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate MongoDB aggregation pipeline from natural language question.
        
        Args:
            question: Natural language question
            schema: Database schema information
            
        Returns:
            MongoDB aggregation pipeline
        """
        
        schema_str = json.dumps(schema, indent=2)
        
        system_prompt = f"""You are an expert MongoDB query generator.
Your task is to convert natural language questions into MongoDB aggregation pipelines.

Database Schema:
{schema_str}

Important Rules:
1. Return ONLY valid MongoDB aggregation pipeline as JSON array
2. Each stage must be a valid MongoDB operator ($match, $group, $sort, $limit, etc.)
3. Use only fields that exist in the schema
4. For money amounts, use the 'total_amount' field
5. For dates, use 'invoice_date' field in YYYY-MM-DD format
6. For months, use the 'month' field which contains month names (January, February, etc.)
7. For years, use the 'year' field which contains year as string (e.g., "2026")
8. Always ensure pipeline is properly formed
9. Return empty array [] if question cannot be converted to a query
10. Do not include explanations or markdown, only JSON

Examples:
Q: "What is the total spent?"
A: [
  {{"$group": {{"_id": null, "total": {{"$sum": "$total_amount"}}}}}}
]

Q: "Show top 5 invoices"
A: [
  {{"$sort": {{"total_amount": -1}}}},
  {{"$limit": 5}}
]

Q: "Group by seller"
A: [
  {{"$group": {{
    "_id": "$seller_name",
    "count": {{"$sum": 1}},
    "total": {{"$sum": "$total_amount"}},
    "average": {{"$avg": "$total_amount"}}
  }}}},
  {{"$sort": {{"total": -1}}}}
]
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"Generate MongoDB aggregation pipeline for: {question}"
                    }
                ]
            )
            
            pipeline_str = response.choices[0].message.content.strip()
            
            # Parse the JSON response
            pipeline = json.loads(pipeline_str)
            
            if not isinstance(pipeline, list):
                return []
            
            return pipeline
        
        except json.JSONDecodeError:
            return []
        except Exception as e:
            raise Exception(f"Error generating query: {str(e)}")
    
    def generate_answer(self, question: str, query_results: Any) -> str:
        """
        Generate natural language answer from query results using LLM.
        
        Args:
            question: Original question
            query_results: Results from MongoDB query
            
        Returns:
            Natural language answer
        """
        
        # Format results for LLM
        if isinstance(query_results, list):
            results_str = json.dumps(query_results, indent=2, default=str)
        else:
            results_str = str(query_results)
        
        system_prompt = """You are an expert at converting database query results into clear, natural language answers.

Your task is to:
1. Analyze the original question
2. Look at the database results
3. Generate a clear, concise human-readable answer
4. Include relevant context (numbers, names, amounts)
5. Format currency as ₹X,XXX.XX
6. Be conversational but informative

Rules:
1. Answer should be 2-3 sentences maximum
2. Include specific numbers from the results
3. Make it easy to understand
4. If results are empty, say "No data found"
5. Don't include technical details unless relevant
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.7,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"""Original Question: {question}

Database Results:
{results_str}

Generate a natural language answer:"""
                    }
                ]
            )
            
            answer = response.choices[0].message.content.strip()
            return answer
        
        except Exception as e:
            raise Exception(f"Error generating answer: {str(e)}")


class LLMQueryPipeline:
    """
    Complete pipeline: Question -> LLM Query -> MongoDB -> LLM Answer
    """
    
    def __init__(self, mongodb_collection):
        """
        Initialize the query pipeline.
        
        Args:
            mongodb_collection: PyMongo collection object
        """
        self.collection = mongodb_collection
        self.query_generator = LLMQueryGenerator()
    
    def get_collection_schema(self) -> Dict[str, Any]:
        """Get schema information from collection."""
        try:
            # Sample documents to understand schema
            sample_docs = list(self.collection.find({}).limit(5))
            
            if not sample_docs:
                return {
                    "fields": [
                        "invoice_number", "invoice_date", "seller_name", 
                        "seller_address", "description", "quantity", 
                        "total_amount", "payment_details"
                    ],
                    "note": "Empty collection - using default schema"
                }
            
            # Extract field names and types
            fields = {}
            for doc in sample_docs:
                for key, value in doc.items():
                    if key not in fields:
                        fields[key] = type(value).__name__
            
            return {
                "fields": list(fields.keys()),
                "sample_types": fields,
                "total_documents": self.collection.count_documents({})
            }
        
        except Exception as e:
            return {"error": str(e)}
    
    def process_question(self, question: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process a natural language question through the complete pipeline.
        
        Args:
            question: Natural language question
            
        Returns:
            Tuple of (answer_string, metadata_dict)
        """
        
        metadata = {
            "question": question,
            "pipeline": None,
            "result_count": 0,
            "error": None
        }
        
        try:
            # Step 1: Get collection schema
            schema = self.get_collection_schema()
            metadata["schema"] = schema
            
            # Step 2: Generate MongoDB pipeline using LLM
            pipeline = self.query_generator.generate_mongodb_query(question, schema)
            
            if not pipeline:
                return (
                    "I couldn't understand that question. Could you rephrase it? "
                    "Try asking about: total spending, invoice counts, highest/lowest amounts, "
                    "top invoices, or breakdowns by seller.",
                    {**metadata, "error": "Could not generate valid MongoDB pipeline"}
                )
            
            metadata["pipeline"] = pipeline
            
            # Step 3: Execute pipeline against MongoDB
            try:
                results = list(self.collection.aggregate(pipeline))
            except Exception as e:
                return (
                    f"Error executing query: {str(e)}",
                    {**metadata, "error": f"MongoDB execution error: {str(e)}"}
                )
            
            metadata["result_count"] = len(results)
            metadata["raw_results"] = results
            
            # Step 4: Generate natural language answer using LLM
            if not results:
                answer = "No data found matching your query."
            else:
                answer = self.query_generator.generate_answer(question, results)
            
            return answer, metadata
        
        except Exception as e:
            return (
                f"Error processing question: {str(e)}",
                {**metadata, "error": str(e)}
            )
