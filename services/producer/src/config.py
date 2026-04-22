from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

JETSTREAM_URL = (
    "wss://jetstream1.us-east.bsky.network/subscribe"
    "?wantedCollections=app.bsky.feed.post"
)

SOURCE_NAME = "bluesky"
SAVE_SAMPLE_PATH = BASE_DIR / "storage" / "data" / "sample_post.json"
MAX_SAMPLE_POSTS = 10000