import json
import re
from collections import Counter, deque
from pathlib import Path
from flask import Flask, jsonify

app = Flask(__name__)

WINDOW_SIZE = 10

BASE_DIR = Path(__file__).resolve().parents[3]
FILE_PATH = BASE_DIR / "storage" / "data" / "sample_post.json"

window = deque(maxlen=WINDOW_SIZE)


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s#]", "", text)
    return text


def extract_keywords(text: str) -> list[str]:
    words = text.split()
    return [word.replace("#", "") for word in words if word.startswith("#")]


def load_posts() -> list:
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading posts: {e}")
        return []


def get_top_trends_from_posts(posts: list) -> list[dict]:
    temp_window = deque(maxlen=WINDOW_SIZE)

    for post in posts[-WINDOW_SIZE:]:
        text = clean_text(post.get("text", ""))
        keywords = extract_keywords(text)
        temp_window.append(keywords)

    all_keywords = [word for sublist in temp_window for word in sublist]
    counter = Counter(all_keywords)

    return [
        {"keyword": word, "count": count}
        for word, count in counter.most_common(5)
    ]


def add_live_post(text: str) -> None:
    cleaned = clean_text(text)
    keywords = extract_keywords(cleaned)
    window.append(keywords)


def get_live_trends() -> list[dict]:
    all_keywords = [word for sublist in window for word in sublist]
    counter = Counter(all_keywords)

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

    top_trends = get_top_trends_from_posts(posts)

    return jsonify({
        "message": "Current top trends retrieved successfully from file data.",
        "window_size": WINDOW_SIZE,
        "total_posts_loaded": len(posts),
        "trends": top_trends
    })


@app.route("/live-trends")
def live_trends():
    return jsonify({
        "message": "Current live trends retrieved successfully.",
        "window_size": WINDOW_SIZE,
        "trends": get_live_trends()
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)