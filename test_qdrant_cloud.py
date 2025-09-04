import os

from qdrant_client import QdrantClient

collection_name = "legi_ro"
qdrant_api_key = os.getenv("QDRANT_API_KEY")
cloud_url = "https://14c4547c-e9c4-4793-ab4a-3834d017892c.europe-west3-0.gcp.cloud.qdrant.io:6333"
local_host_url = "http://localhost:31333/"
client = QdrantClient(
    url=cloud_url,
    api_key=qdrant_api_key,
    timeout=7200, # 2 hours timeout
    check_compatibility=False,
)

if client.collection_exists(collection_name):
    print("can make calls to cloud from ntt data laptop")