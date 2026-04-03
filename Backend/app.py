from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import requests
import re

# ----- SUMMARY LIBRARIES -----
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# ----- TRANSLATION -----
from deep_translator import GoogleTranslator

app = Flask(__name__)
CORS(app)


# -------------------------------------------------
# Clean transcript text
# -------------------------------------------------
def clean_transcript(text):
    text = text.replace("Kind: captions", "")
    text = re.sub(r"Language: [a-zA-Z\-]+", "", text)
    text = re.sub(r"<.*?>", "", text)           # remove HTML/XML tags
    text = re.sub(r"\[.*?\]", "", text)         # remove [Music], etc
    text = re.sub(r'\b(\w+)( \1\b)+', r'\1', text)  # repeated words
    text = re.sub(r"\s+", " ", text)           # extra spaces
    return text.strip()


# -------------------------------------------------
# Translate any language to English
# -------------------------------------------------
def translate_to_english(text):
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except:
        return text


# -------------------------------------------------
# Merge incremental captions to remove duplicates
# -------------------------------------------------
def merge_captions(transcript_list):
    text = ""
    last_words = []

    for item in transcript_list:
        line = item['text'].strip()
        if not line:
            continue

        words = line.split()
        overlap_len = 0
        for i in range(1, min(len(words), len(last_words)) + 1):
            if words[:i] == last_words[-i:]:
                overlap_len = i
        words = words[overlap_len:]
        last_words += words
        text += " " + " ".join(words)

    return text.strip()


# -------------------------------------------------
# Generate summary
# -------------------------------------------------
def summarize(text):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()

    sentences = text.split(".")
    length = len(sentences)

    if length < 30:
        size = 2
    elif length < 80:
        size = 4
    elif length < 150:
        size = 6
    else:
        size = 10

    summary_sentences = summarizer(parser.document, size)
    result = " ".join(str(s) for s in summary_sentences)
    if not result.strip():
        result = text[:200]

    return result


# -------------------------------------------------
# Home route
# -------------------------------------------------
@app.route("/")
def home():
    return "Backend Running"


# -------------------------------------------------
# Transcript + Summary API
# -------------------------------------------------
@app.route("/transcript")
def get_transcript():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Please provide YouTube URL"})

    try:
        # yt-dlp options
        ydl_opts = {
            "writesubtitles": True,
            "writeautomaticsub": True,
            "skip_download": True,
            "subtitleslangs": ["en", "en-US"],
            "quiet": True
        }

        # get video info
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "video")

        # Try manual subtitles first, then automatic captions
        subtitles = info.get("subtitles") or info.get("automatic_captions")
        if not subtitles or "en" not in subtitles:
            return jsonify({"error": "No subtitles available for this video"})

        # Fetch subtitle text directly from URL
        subtitle_url = subtitles["en"][0]["url"]
        res = requests.get(subtitle_url)
        transcript_lines = res.text.splitlines()

        # Convert lines into a list of dicts like before
        transcript_list = [{"text": line.strip()} for line in transcript_lines if line.strip() and "-->" not in line and "WEBVTT" not in line]

        # Merge incremental captions
        merged_text = merge_captions(transcript_list)

        # Clean transcript
        clean_text = clean_transcript(merged_text)

        # Translate if not English
        clean_text = translate_to_english(clean_text)

        # Generate summary
        summary = summarize(clean_text)

        return jsonify({
            "title": title,
            "transcript": clean_text,
            "summary": summary
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# -------------------------------------------------
# Run Flask server
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)