import os


SOURCE_NAME = "bluesky"
JETSTREAM_URLS = [
    "wss://jetstream1.us-east.bsky.network/subscribe",
    "wss://jetstream2.us-east.bsky.network/subscribe",
    "wss://jetstream1.us-west.bsky.network/subscribe",
    "wss://jetstream2.us-west.bsky.network/subscribe",
]
JETSTREAM_INDEX = int(os.getenv("JETSTREAM_INDEX", "3"))

LOCAL_SAMPLE_PATH = "services/ingestion/logs/post_dump.json"
MAX_SAMPLE_POSTS = int(os.getenv("MAX_SAMPLE_POSTS", "200"))
RECONNECT_DELAY_SECONDS = float(os.getenv("RECONNECT_DELAY_SECONDS", "5"))
MAX_RECONNECT_DELAY_SECONDS = float(os.getenv("MAX_RECONNECT_DELAY_SECONDS", "60"))
RECONNECT_BACKOFF_MULTIPLIER = float(os.getenv("RECONNECT_BACKOFF_MULTIPLIER", "2"))


__all__ = [
    "SOURCE_NAME",
    "JETSTREAM_URLS",
    "JETSTREAM_INDEX",
    "LOCAL_SAMPLE_PATH",
    "MAX_SAMPLE_POSTS",
    "RECONNECT_DELAY_SECONDS",
    "MAX_RECONNECT_DELAY_SECONDS",
    "RECONNECT_BACKOFF_MULTIPLIER",
]
