from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import pdfplumber
import faiss
import numpy as np
import uuid
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)

from flask_cors import CORS

CORS(
    app,
    resources={r"/*": {"origins": [
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://research-assistant.web.app"
    ]}},
    supports_credentials=True
)

client = OpenAI(
    base_url= "https://openrouter.ai/api/v1",
    api_key= os.getenv("OPEN_API_KEY")
)

documents = {}


def extract_text(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def chunk_text(text, chunk_size=800):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def get_overview(text):
    extract_prompt = """
    Extract the following information from the paper in strict JSON format:

    {
    "authors": "",
    "year": "",
    "title": "",
    "objectives": "",
    "methods": "",
    "results": "",
    "limitations": ""
    }

    If information is missing, return null.
    Do not add commentary.
    """

    summary_prompt = """ 
    Using the structured data below, write exactly one cohesive academic paragraph under 200 words.

    Use academic transition phrases (e.g.,'John Doe et al. (2001) proposed....' , 'The primary goal of (John Doe et al. 2001)...','The system aims to...', 'The system uses...',  'The study explores...', 'Utilizing a methodology of...', 'The findings reveal...', 'The major drawback...' and other phrases) to ensure a fluid narrative and include any other critical unique insights found in the paper.
    If null, do not invent data to fill
    No bullet points.
    No line breaks.

    Structured Data:
    {json_output}
    """

    extract = client.chat.completions.create(
        model = "meta-llama/llama-3.3-70b-instruct",
        temperature=0.1,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": extract_prompt},
            {"role": "user", "content": text}
        ]
    )

    json_output = extract.choices[0].message.content
    review = client.chat.completions.create(
        model = "meta-llama/llama-3.3-70b-instruct",
        temperature=0.1,
        messages=[
            {"role": "system", "content": summary_prompt},
            {"role": "user", "content": json_output}
        ]
    )
    return review.choices[0].message.content


def ask_llm(question, context):
    prompt = f"""
    Use the following context to answer the question.

    Context:
    {context}

    Question:
    {question}
    """

    response = client.chat.completions.create(
        model="meta-llama/llama-3.3-70b-instruct",
        temperature= 0.2,
        messages=[
            {"role": "system", "content": "You answer questions strictly from provided context."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    upload_id = str(uuid.uuid4())

    file_path = f"temp_{upload_id}.pdf"
    file.save(file_path)

    text = extract_text(file_path)
    os.remove(file_path)

    chunks = chunk_text(text)
    embeddings = [get_embedding(chunk) for chunk in chunks]

    dimension = len(embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype("float32"))

    documents[upload_id] = {
        "chunks": chunks,
        "index": index
    }

    overview = get_overview(text=text)

    return jsonify({
        "upload_id": upload_id,
        "overview": overview
    })


@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    upload_id = data["upload_id"]
    question = data["question"]

    doc = documents.get(upload_id)

    if not doc:
        return jsonify({"error": "Upload first"}), 400

    question_embedding = get_embedding(question)

    D, I = doc["index"].search(
        np.array([question_embedding]).astype("float32"), 5
    )

    context = "\n\n".join([doc["chunks"][i] for i in I[0]])

    answer = ask_llm(question, context)

    return jsonify({"answer": answer})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)