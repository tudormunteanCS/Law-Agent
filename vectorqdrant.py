from qdrant_client import QdrantClient
import os

qdrant_client = QdrantClient(
    url="https://14c4547c-e9c4-4793-ab4a-3834d017892c.europe-west3-0.gcp.cloud.qdrant.io:6333",
    api_key=os.getenv('QDRANT_API_KEY'),
)

print(qdrant_client.get_collections())
