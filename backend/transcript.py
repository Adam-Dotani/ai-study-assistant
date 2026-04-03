import os
import re

from youtube_transcript_api import YouTubeTranscriptApi
import PyPDF2

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def get_transcript(video_id):
    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id)

    text = " ".join([t.text for t in transcript])
    return text


def save_transcript(text, filename):
    os.makedirs(DATA_DIR, exist_ok=True)
    if not filename.endswith(".txt"):
        filename = filename + ".txt"
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def load_transcript(filename):
    if not filename.endswith(".txt"):
        filename = filename + ".txt"
    path = os.path.join(DATA_DIR, filename)
    with open(path, encoding="utf-8") as f:
        return f.read()


def extract_pdf_text(file_path):
    text = ""

    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""

    return " ".join(text.split())