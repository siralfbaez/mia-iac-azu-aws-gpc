import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()

class SecureSearchService:
    def __init__(self):
        self.es = Elasticsearch(
            cloud_id=os.getenv("ELASTIC_CLOUD_ID"),
            api_key=os.getenv("ELASTIC_API_KEY")
        )

    def execute_secure_search(self, user_query, user_roles):
        """
        Executes a search that automatically filters by user roles.
        This is the 'Late-Binding' logic that satisfies the ARB.
        """

        # This is where we combine the search intent with the security shield
        query_body = {
            "query": {
                "bool": {
                    "must": [
                        # 1. The Search Intent (Keyword or Semantic)
                        { "match": { "content_body": user_query } }
                    ],
                    "filter": [
                        # 2. The Security Filter (The Shield)
                        # Only return docs where the user's role exists in _iam_access_control
                        { "terms": { "_iam_access_control": user_roles } }
                    ]
                }
            }
        }

        response = self.es.search(index="enterprise-knowledge-v1", body=query_body)
        return response['hits']['hits']

# --- Mock Scenario ---
# Let's say Alf is searching, but he only has 'loan-officer-fl' permissions.
search_service = SecureSearchService()
results = search_service.execute_secure_search(
    user_query="disaster relief",
    user_roles=["loan-officer-fl"]
)

for hit in results:
    print(f"Result Found: {hit['_source']['title']} (Score: {hit['_score']})")