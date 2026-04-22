import json
import re
from collections import Counter, deque
from pathlib import Path
from flask import Flask, jsonify

app = Flask(__name__)

WINDOW_SIZE = 10

BASE_DIR = Path(__file__).resolve().parents[3]
FILE_PATH = BASE_DIR / "storage" / "data" / "sample_post.json"

STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "is", "it",
    "this", "that", "with", "as", "at", "by", "be", "are", "was", "were",
    "from", "our", "your", "their", "have", "has", "had", "but", "not",
    "you", "they", "we", "he", "she", "i", "me", "my", "us", "them",
    "if", "so", "all", "too", "just", "out", "up", "down", "into", "about",
    "when", "what", "where", "there", "then", "than", "more", "most",
    "using", "based", "framework", "system", "study", "paper", "issue",
    "also", "through", "current", "currently", "another", "some", "like",
    "around", "friend", "thanks", "email", "customer", "apologies"
}

BLOCKLIST = {
    "wang", "jiashuo", "jiawen", "johnny", "brkljavc", "kalu", "konishi",
    "tsubouchi", "tsuruta", "duan", "song", "xu", "li", "yu", "liu"
}

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^\w\s#]", "", text)
    return text


def extract_hashtags(text: str) -> list[str]:
    return re.findall(r"#(\w+)", text)


def extract_keywords(text: str) -> list[str]:
    words = text.split()
    keywords = []

    for word in words:
        if word.startswith("#"):
            continue
        if len(word) < 4:
            continue
        if word in STOPWORDS:
            continue
        if word in BLOCKLIST:
            continue
        if word.isdigit():
            continue
        if re.search(r"\d", word):
            continue
        keywords.append(word)

    return keywords


def load_posts() -> list:
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading posts: {e}")
        return []


def get_top_trends(posts: list) -> list[dict]:
    temp_window = deque(maxlen=WINDOW_SIZE)

    for post in posts[-WINDOW_SIZE:]:
        text = clean_text(post.get("text", ""))

        hashtags = extract_hashtags(text)
        if hashtags:
            terms = hashtags
        else:
            terms = extract_keywords(text)

        temp_window.append(terms)

    all_terms = [word for sublist in temp_window for word in sublist]
    counter = Counter(all_terms)

    return [
        {"keyword": word, "count": count}
        for word, count in counter.most_common(5)
    ]


@app.route("/")
def home():
    return jsonify({
        "service": "trend_service",
        "status": "running",
        "endpoints": ["/trends"]
    })


@app.route("/trends")
def trends():
    posts = load_posts()

    if not posts:
        return jsonify({
            "message": "No data found yet.",
            "trends": []
        }), 200

    top_trends = get_top_trends(posts)

    return jsonify({
        "message": "Current top trends retrieved successfully from file data.",
        "window_size": WINDOW_SIZE,
        "total_posts_loaded": len(posts),
        "trends": top_trends
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)