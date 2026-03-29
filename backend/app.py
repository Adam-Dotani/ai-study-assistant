import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

from ppt_extract import DATA_DIR as PPT_DATA_DIR, get_ppt_text, save_ppt_text
from transcript import get_transcript, load_transcript, save_transcript

load_dotenv()

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@app.route("/load_video", methods=["POST"])
def load_video():
    data = request.get_json()
    if not data or "video_id" not in data:
        return jsonify({"error": "Missing 'video_id' in request body"}), 400

    video_id = data["video_id"]
    text = get_transcript(video_id)
    save_transcript(text, "lecture.txt")
    return jsonify({"message": "Lecture transcript loaded successfully."})


@app.route("/load_ppt", methods=["POST"])
def load_ppt():
    if "file" not in request.files:
        return jsonify({"error": "Missing 'file' in request (multipart form)"}), 400
    f = request.files["file"]
    if not f.filename or not f.filename.lower().endswith(".pptx"):
        return jsonify({"error": "Upload a .pptx file"}), 400

    upload_path = os.path.join(PPT_DATA_DIR, "_upload.pptx")
    os.makedirs(PPT_DATA_DIR, exist_ok=True)
    f.save(upload_path)
    try:
        text = get_ppt_text(upload_path)
        save_ppt_text(text, "lecture.txt")
    finally:
        if os.path.isfile(upload_path):
            os.remove(upload_path)

    return jsonify({"message": "Lecture extracted from PowerPoint successfully."})


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"error": "Missing 'question' in request body"}), 400

    question = data["question"]
    try:
        lecture_text = load_transcript("lecture.txt")
    except FileNotFoundError:
        return jsonify(
            {
                "error": "No lecture loaded. POST to /load_video or /load_ppt first."
            }
        ), 400

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "Use the following lecture content to answer the question:\n\n"
                + lecture_text,
            },
            {"role": "user", "content": question},
        ],
    )
    answer = response.choices[0].message.content
    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=True)
