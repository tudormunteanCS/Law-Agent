import json
from pathlib import Path
from qdrant_client import QdrantClient
import os
import itertools
from qdrant_client.http import models as qdrant
from tqdm import tqdm
from openai import OpenAI
import uuid


# qdrant_client = QdrantClient(
#     url="https://14c4547c-e9c4-4793-ab4a-3834d017892c.europe-west3-0.gcp.cloud.qdrant.io:6333",
#     api_key=qdrant_api_key,
#     check_compatibility=False
# )
# print(qdrant_client.get_collections())

def create_collection(client, collection_name, DIMENSIONS):
    if not client.collection_exists(collection_name):
        print(f"Collection {collection_name} does not exist. Creating it...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=qdrant.VectorParams(
                size=DIMENSIONS,
                distance=qdrant.Distance.COSINE
            ),
            optimizers_config=qdrant.OptimizersConfigDiff(
                memmap_threshold=200_000,  # performant pt. >200k puncte
            ),
        )


def chunked(iterable, n):
    it = iter(iterable)
    while True:
        chunk = list(itertools.islice(it, n))
        if not chunk:
            break
        yield chunk


def embedd_texts(texts, openai_api_key, dimensions):
    client = OpenAI(
        api_key=openai_api_key
    )
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
        dimensions=dimensions,
        encoding_format="float"
    )
    return [embedding['embedding'] for embedding in resp['data']]  # Extract embeddings from response


if __name__ == "__main__":
    openai_api_key = os.getenv("OPENAI_API_KEY")
    qdrant_api_key = os.getenv('QDRANT_API_KEY')
    data = Path("processed_data")
    collection_name = "legi_ro"
    DIMENSIONS = 1536
    BATCH_SIZE = 300

    client = QdrantClient(
        url="https://14c4547c-e9c4-4793-ab4a-3834d017892c.europe-west3-0.gcp.cloud.qdrant.io:6333",
        api_key=qdrant_api_key,
        timeout=60,
        check_compatibility=False,
    )
    # creating the collection only ran once
    create_collection(client, collection_name, DIMENSIONS)
    all_files = list(data.glob("*.json"))
    for file_path in tqdm(all_files):
        with open(file_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        for batch in chunked(json_data, BATCH_SIZE):
            texts = [chunk["text"] for chunk in batch]
            vectors = embedd_texts(texts, openai_api_key, DIMENSIONS)
            payloads = [
                {
                    "sursa": chunk["sursa"],
                    "articol": chunk["articol"],
                    "aliniat": chunk["alin"],
                    "text": chunk["text"],
                } for chunk in batch
            ]
            # construct list of ids
            ids = [uuid.uuid4() for chunk in batch]

            client.upsert(
                collection_name=collection_name,
                points=qdrant.Batch(
                    ids=ids,
                    vectors=vectors,
                    payloads=payloads
                )
            )
