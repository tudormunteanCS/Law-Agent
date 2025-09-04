# server.py
import json
import os
import textwrap
import time

from flask import Flask, request, jsonify
from flask_cors import CORS
from qdrant_client import QdrantClient
from vectorqdrant import embedd_texts
from openai import OpenAI

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
DIMENSIONS = 1536
OPENAI_API_KEY = os.getenv("OPENAI_Lawgentic_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

local_host_url = "http://localhost:31333/"
collection_name = "legi_ro"
#localhost version (endava pc)

# client = QdrantClient(
#     url=local_host_url,
#     check_compatibility=False,
# )

#cloud version
qdrant_api_key = os.getenv("QDRANT_API_KEY")
cloud_url = "https://14c4547c-e9c4-4793-ab4a-3834d017892c.europe-west3-0.gcp.cloud.qdrant.io:6333"
client = QdrantClient(
    url=cloud_url,
    api_key=qdrant_api_key,
    check_compatibility=False,
)


@app.route("/")
def home():
    return "Hello, World!"


def retrieve_top_k_points(embedded_question, k=7):
    """
    Qdrant API call to retrieve top k similar semantic points from Qdrant
    :param embedded_question:
    :param k:
    :return:
    """
    # retrieve top k vectors from Qdrant
    results = client.query_points(
        collection_name=collection_name,
        query=embedded_question,
        with_payload=True,
        limit=k,
    )
    return results.points


def build_context(best_points_payload: list[dict]):
    """
    stringify the best k points from payload and build a context for LLM
    :param best_points_payload:
    :return:
    """
    blocks = []
    for point in best_points_payload:
        json_point = json.dumps(point, ensure_ascii=False)
        blocks.append(json_point)

    context = "\n\n".join(blocks)
    return context


def extract_answer_from_llm(best_points_payload, question):
    """
    Extracts an answer from the LLM based on the best k points from payload.
    :param best_points_payload: Top 10 most relevant semantic points from Qdrant
    :param question: The original question asked by the user
    :return: AI-generated answer based on the best points
    """
    context = build_context(best_points_payload)
    system_msg = (
        "Ești un asistent virtual in domeniul juridic care răspunde la întrebări legate de legislația românească."
        "Răspunde la întrebări STRICT folosind informațiile din contextul furnizat. Dacă contextul este insuficient, spune că nu ai suficiente informații pentru a răspunde la întrebare."
        "Pentru fiecare răspuns pune citații din contextul dat, precum și sursa, articolul și alineatul, dacă este cazul."
        "Vreau un răspuns concis și la obiect."
    )
    instructiuni = textwrap.dedent(f"""
    INSTRUCȚIUNI: {system_msg}
    ÎNTREBARE: {question}
    CONTEXT: {repr(context)}
    """)
    response = openai_client.responses.create(
        model="gpt-5-nano",
        input=instructiuni,
        top_p=1.0,
        reasoning={
            "effort": "low"
        },
        text={
            "verbosity": "low"
        }
    )
    return response.output_text


def process(question):
    """
    RAG workflow. Embeds the question, retrieves top k points from Qdrant, and extracts an answer from the LLM.
    :param question: The question to be answered string
    :return: answer from the LLM
    """
    embedd_start_time = time.perf_counter()
    embedded_question = embedd_texts(texts=question, openai_api_key=OPENAI_API_KEY, dimensions=DIMENSIONS)
    embedd_end_time = time.perf_counter()
    print(f"Embedding time: {embedd_end_time - embedd_start_time:.4f} seconds")

    qdrant_retrieval_start_time = time.perf_counter()
    top_k_points = retrieve_top_k_points(embedded_question)
    qdrant_retrieval_end_time = time.perf_counter()
    print(f"Qdrant retrieval time: {qdrant_retrieval_end_time - qdrant_retrieval_start_time:.4f} seconds")

    # Extract payloads
    best_points_payload = [x.payload for x in top_k_points]

    llm_start_time = time.perf_counter()
    answer = extract_answer_from_llm(best_points_payload, question)
    llm_end_time = time.perf_counter()
    print(f"LLM processing time: {llm_end_time - llm_start_time:.4f} seconds")
    return answer


def log_req(duration_ms, question, answer):
    """
    create a json with duration question and answer and log to a file by appending the data
    :param duration_ms:
    :param question:
    :param answer:
    :return:
    """
    time_now = time.ctime()
    log_data = {
        "duration_ms": duration_ms,
        "question": question,
        "answer": answer,
        "timestamp": time_now
    }
    with open("request_logs.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_data, ensure_ascii=False) + "\n")


@app.route("/answer", methods=["POST"])
def answer_question():
    """
    A simple endpoint that returns an answer to a question.
    :return:
    """
    data = request.get_json(silent=True) or {}
    question = data.get("question")
    start_time = time.perf_counter()
    try:
        answer = process(question)
        return jsonify({"question": question, "answer": answer})
    finally:
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        log_req(duration_ms, question, answer)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, port=5000, threaded=True)
