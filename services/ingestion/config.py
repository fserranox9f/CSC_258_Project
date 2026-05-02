
SOURCE_NAME = "bluesky"
JETSTREAM_URLS = [
    "wss://jetstream1.us-east.bsky.network/subscribe",
    "wss://jetstream2.us-east.bsky.network/subscribe",
    "wss://jetstream1.us-west.bsky.network/subscribe",
    "wss://jetstream2.us-west.bsky.network/subscribe",
]
JETSTREAM_INDEX = 3

LOCAL_SAMPLE_PATH = "services\ingestion\logs\post_dump.json"
MAX_SAMPLE_POSTS = 200


__all__ = [
    "SOURCE_NAME",
    "JETSTREAM_URLS",
    "JETSTREAM_INDEX",
    "LOCAL_SAMPLE_PATH",
    "MAX_SAMPLE_POSTS",
]
