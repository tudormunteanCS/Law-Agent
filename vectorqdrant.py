import json
from pathlib import Path
from qdrant_client import QdrantClient
import os
import itertools
from qdrant_client.http import models as qdrant
from tqdm import tqdm
from openai import OpenAI
import uuid


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
    else:
        print("Collection: " + collection_name + " already exists.")


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
    ).data[0].embedding
    return resp


if __name__ == "__main__":
    openai_api_key = os.getenv("OPENAI_Lawgentic_API_KEY")
    client = OpenAI(api_key=openai_api_key)
    qdrant_api_key = os.getenv('QDRANT_API_KEY')
    data = Path("processed_data")
    collection_name = "legi_ro"
    DIMENSIONS = 1536

    cloud_url = "https://14c4547c-e9c4-4793-ab4a-3834d017892c.europe-west3-0.gcp.cloud.qdrant.io:6333"
    local_host_url = "http://localhost:31333/"
    client = QdrantClient(
        url=local_host_url,
        # api_key=qdrant_api_key,
        timeout=7200, # 2 hours timeout
        check_compatibility=False,
    )
    # creating the collection only ran once
    create_collection(client, collection_name, DIMENSIONS)
    all_files = list(data.glob("*.json"))

    for file_path in tqdm(all_files):
        ids = []
        payloads = []
        vectors = []
        with open(file_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        length = len(json_data)
        count = 1
        for chunk in json_data:
            print(f"Processing {file_path.name} {count}/{length}")
            text = chunk["text"]
            vectors.append(embedd_texts(text, openai_api_key, DIMENSIONS))
            payloads.append(
                {
                    "sursa": chunk["sursa"],
                    "articol": chunk["articol"],
                    "aliniat": chunk["alin"],
                    "text": chunk["text"],
                }
            )
            ids.append(str(uuid.uuid4()))
            count += 1
        # use the chunked method to upsert in batches
        for batch in chunked(zip(ids, vectors, payloads), 500):
            ids_batch, vectors_batch, payloads_batch = zip(*batch)
            client.upsert(
                collection_name=collection_name,
                points=qdrant.Batch(
                    ids=list(ids_batch),
                    vectors=list(vectors_batch),
                    payloads=list(payloads_batch)
                )
            )
            print(f"Upserted {len(ids_batch)} points from {file_path.name} to collection {collection_name}.")


