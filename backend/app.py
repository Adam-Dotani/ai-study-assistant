import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

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
            {"error": "No lecture loaded. POST to /load_video with a video_id first."}
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
