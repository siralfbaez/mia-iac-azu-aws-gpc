import os
from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

# Load your "Security Shield" configuration
load_dotenv()

class SearchIntelligenceAgent:
    def __init__(self):
        # Initialize Vertex AI
        aiplatform.init(project=os.getenv("GCP_PROJECT_ID"), location=os.getenv("GCP_REGION"))
        self.model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")

        # Initialize Elasticsearch
        self.es = Elasticsearch(
            cloud_id=os.getenv("ELASTIC_CLOUD_ID"),
            api_key=os.getenv("ELASTIC_API_KEY")
        )

    def generate_embeddings(self, text):
        """Converts raw text into a 768-dimension vector."""
        embeddings = self.model.get_embeddings([text])
        return embeddings[0].values

    def ingest_document(self, doc_id, title, content, roles, legacy_meta=None):
        """Prepares and pushes the document with IAM security."""

        # 1. Generate the 'Brain' of the document
        vector = self.generate_embeddings(content)

        # 2. Construct the Payload (Matching our Schema)
        payload = {
            "doc_id": doc_id,
            "title": title,
            "content_body": content,
            "_iam_access_control": roles, # The ARB Security Filter
            "content_vector": vector,
            "legacy_context": legacy_meta or {},
            "source_system": "SBA_Mainframe_Legacy"
        }

        # 3. Index to Elastic
        response = self.es.index(index="enterprise-knowledge-v1", id=doc_id, document=payload)
        return response

# --- Example Usage (The "SBA" Scenario) ---
agent = SearchIntelligenceAgent()

# Simulated data from your legacy Unisys/COBOL stream
legacy_data = {
    "doc_id": "SBA-LOAN-9982",
    "title": "Disaster Relief Application - Florida Region",
    "content": "Loan application for small business relief following high-wind events.",
    "roles": ["sba-admin", "loan-officer-fl"],
    "legacy_meta": {
        "original_encoding": "EBCDIC",
        "mainframe_job_id": "TX-990",
        "conversion_status": "SUCCESS"
    }
}

agent.ingest_document(**legacy_data)
print(f"Document {legacy_data['doc_id']} indexed with AI embeddings.")