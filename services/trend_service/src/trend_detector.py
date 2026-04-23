import json
import re
import time
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
    "also", "through", "current", "currently", "another", "some", "like",
    "around", "friend", "thanks", "email", "customer", "apologies"
}

BLOCKLIST = {
    "wang", "jiashuo", "jiawen", "johnny", "brkljavc", "kalu", "konishi",
    "tsubouchi", "tsuruta", "duan", "song", "xu", "li", "yu", "liu",
    "framework", "system", "study", "paper", "issue", "using", "based"
}

live_window = deque(maxlen=WINDOW_SIZE)


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^\w\s#]", "", text)
    return text


def extract_hashtags(text: str) -> list[str]:
    return re.findall(r"#(\w+)", text)


def is_candidate_trend_word(word: str) -> bool:
    if word.startswith("#"):
        return False
    if len(word) < 4:
        return False
    if not word.isalpha():
        return False
    if word in STOPWORDS:
        return False
    if word in BLOCKLIST:
        return False
    return True


def extract_keywords(text: str) -> list[str]:
    words = text.split()
    return [word for word in words if is_candidate_trend_word(word)]


def extract_terms(text: str) -> list[str]:
    hashtags = extract_hashtags(text)
    if hashtags:
        return hashtags
    return extract_keywords(text)


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
        terms = extract_terms(text)
        temp_window.append(terms)

    all_terms = [word for sublist in temp_window for word in sublist]
    counter = Counter(all_terms)

    return [
        {"keyword": word, "count": count}
        for word, count in counter.most_common(5)
    ]


def add_live_post(text: str) -> None:
    cleaned = clean_text(text)
    terms = extract_terms(cleaned)
    live_window.append(terms)


def get_live_trends() -> list[dict]:
    all_terms = [word for sublist in live_window for word in sublist]
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
        "endpoints": ["/trends", "/live-trends"]
    })


@app.route("/trends")
def trends():
    posts = load_posts()

    if not posts:
        return jsonify({
            "message": "No data found yet.",
            "trends": []
        }), 200

    start = time.perf_counter()
    top_trends = get_top_trends(posts)
    elapsed = time.perf_counter() - start

    return jsonify({
        "message": "Current top trends retrieved successfully from file data.",
        "window_size": WINDOW_SIZE,
        "total_posts_loaded": len(posts),
        "processing_time_seconds": round(elapsed, 6),
        "trends": top_trends
    })


@app.route("/live-trends")
def live_trends():
    start = time.perf_counter()
    top_trends = get_live_trends()
    elapsed = time.perf_counter() - start

    return jsonify({
        "message": "Current live trends retrieved successfully.",
        "window_size": WINDOW_SIZE,
        "processing_time_seconds": round(elapsed, 6),
        "trends": top_trends
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)