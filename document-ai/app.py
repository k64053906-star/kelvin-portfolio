from flask import Flask, render_template, request
import os
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def extract_text(file):
    filename = file.filename.lower()

    if filename.endswith(".txt"):
        return file.read().decode("utf-8", errors="ignore")

    if filename.endswith(".pdf"):
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(file)
            pages = []
            for page in reader.pages:
                pages.append(page.extract_text() or "")
            return "\n".join(pages)
        except Exception:
            return "PDF extraction could not be completed. Please try a TXT file."

    return ""


def summarize_text(text):
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return "No document text was found."

    sentences = re.split(r"(?<=[.!?])\s+", text)

    selected = sentences[:5]

    return " ".join(selected)


def extract_key_points(text):
    sentences = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text).strip())

    points = []

    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 30:
            points.append(sentence)

        if len(points) >= 5:
            break

    return points


def answer_question(text, question):
    if not question.strip():
        return "Enter a question about the document."

    words = [
        word.lower()
        for word in re.findall(r"[A-Za-z0-9]+", question)
        if len(word) > 3
    ]

    sentences = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text).strip())

    matches = []

    for sentence in sentences:
        lower_sentence = sentence.lower()
        score = sum(1 for word in words if word in lower_sentence)

        if score > 0:
            matches.append((score, sentence))

    matches.sort(reverse=True, key=lambda item: item[0])

    if matches:
        return " ".join(sentence for _, sentence in matches[:3])

    return "I could not find a strong answer in the document."


@app.route("/")
def index():
    return render_template(
        "index.html",
        document_name=None,
        summary=None,
        key_points=[],
        answer=None,
        question=""
    )


@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files.get("document")
    question = request.form.get("question", "").strip()

    if not file or file.filename == "":
        return render_template(
            "index.html",
            document_name=None,
            summary="Please choose a PDF or TXT document.",
            key_points=[],
            answer=None,
            question=question
        )

    filename = secure_filename(file.filename)

    if not filename.lower().endswith((".pdf", ".txt")):
        return render_template(
            "index.html",
            document_name=filename,
            summary="Unsupported file type. Please upload a PDF or TXT file.",
            key_points=[],
            answer=None,
            question=question
        )

    text = extract_text(file)

    summary = summarize_text(text)
    key_points = extract_key_points(text)
    answer = answer_question(text, question) if question else None

    return render_template(
        "index.html",
        document_name=filename,
        summary=summary,
        key_points=key_points,
        answer=answer,
        question=question
    )


@app.route("/health")
def health():
    return {"status": "ok", "application": "AI Business Document Assistant"}


if __name__ == "__main__":
    app.run(debug=True)
