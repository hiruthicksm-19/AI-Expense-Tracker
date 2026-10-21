
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


class MongoDBHandler:
    def __init__(self):
        self.client = MongoClient(
            os.getenv(
                "MONGODB_URI",
                "mongodb://localhost:27017"
            ),
            serverSelectionTimeoutMS=5000
        )

        self.client.admin.command("ping")

        database_name = os.getenv(
            "MONGODB_DATABASE",
            "invoice_tracker"
        )

        collection_name = os.getenv(
            "MONGODB_COLLECTION",
            "invoices"
        )

        self.db = self.client[database_name]
        self.collection = self.db[collection_name]

        print("Connected to MongoDB successfully.")

    def insert_invoice(self, invoice):
        """Insert one extracted invoice document."""
        document = invoice.copy()

        # Allow MongoDB to generate the ObjectId.
        document.pop("_id", None)

        result = self.collection.insert_one(document)

        print(f"Invoice saved. MongoDB ID: {result.inserted_id}")

        return result.inserted_id

    def insert_many_invoices(self, invoices):
        """Insert multiple extracted invoice documents."""
        if not invoices:
            print("No invoices to insert.")
            return []

        documents = []

        for invoice in invoices:
            document = invoice.copy()
            document.pop("_id", None)
            documents.append(document)

        result = self.collection.insert_many(documents)

        print(f"Inserted {len(result.inserted_ids)} invoices.")

        return result.inserted_ids

    def invoice_exists(self, invoice_number):
        """Check if an invoice with the given invoice_number already exists."""
        if not invoice_number:
            return False
        
        result = self.collection.find_one(
            {"invoice_number": invoice_number}
        )
        
        return result is not None

    def close(self):
        self.client.close()
