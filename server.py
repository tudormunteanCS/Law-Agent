# server.py
import json
import os
import textwrap

from flask import Flask, request, jsonify
from flask_cors import CORS
from qdrant_client import QdrantClient
from vectorqdrant import embedd_texts
from openai import OpenAI

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
DIMENSIONS = 1536
OPENAI_API_KEY = os.getenv("OPENAI_Lawgentic_API_KEY")
local_host_url = "http://localhost:31333/"
collection_name = "legi_ro"

client = QdrantClient(
    url=local_host_url,
    check_compatibility=False,
)

openai_client = OpenAI(api_key=OPENAI_API_KEY)


@app.route("/")
def home():
    return "Hello, World!"


def retrieve_top_k_points(embedded_question, k=10):
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
    :param question:
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

    )
    instructiuni = textwrap.dedent(f"""
    INSTRUCȚIUNI: {system_msg}
    ÎNTREBARE: {question}
    CONTEXT: {repr(context)}
    """)
    response = openai_client.responses.create(
        model="gpt-5",
        input=instructiuni,
    )
    return response.output_text


def process(question):
    embedded_question = embedd_texts(texts=question, openai_api_key=OPENAI_API_KEY, dimensions=DIMENSIONS)
    top_k_points = retrieve_top_k_points(embedded_question)
    best_points_payload = [x.payload for x in top_k_points]
    answer = extract_answer_from_llm(best_points_payload, question)
    return answer


@app.route("/answer", methods=["POST"])
def answer_question():
    """
    A simple endpoint that returns an answer to a question.
    :return:
    """
    data = request.get_json(silent=True) or {}
    question = data.get("question")
    answer = process(question)
    return jsonify({"question": question, "answer": answer})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
