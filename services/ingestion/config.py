import os

#------------------------
# source settings/ server
#------------------------
SOURCE_NAME = os.getenv("SOURCE_NAME","bluesky")

DEFAULT_JETSTREAM_URLS = [
    "wss://jetstream1.us-east.bsky.network/subscribe",
    "wss://jetstream2.us-east.bsky.network/subscribe",
    "wss://jetstream1.us-west.bsky.network/subscribe",
    "wss://jetstream2.us-west.bsky.network/subscribe",
]

JETSTREAM_URLS = [
    url.strip()
    for url in os.getenv("JETSTREAM_URLS", ",".join(DEFAULT_JETSTREAM_URLS)).split(",")
    if url.strip()
]

JETSTREAM_INDEX = int(os.getenv("JETSTREAM_INDEX", "3"))

#------------------------
# reconnection backoff time
#------------------------
RECONNECT_DELAY_SECONDS = float(os.getenv("RECONNECT_DELAY_SECONDS", "5"))
MAX_RECONNECT_DELAY_SECONDS = float(os.getenv("MAX_RECONNECT_DELAY_SECONDS", "60"))
RECONNECT_BACKOFF_MULTIPLIER = float(os.getenv("RECONNECT_BACKOFF_MULTIPLIER", "2"))
MAX_RECONNECT_ATTEMPTS_BEFORE_SWITCH = int(os.getenv("MAX_RECONNECT_ATTEMPTS_BEFORE_SWITCH", "4"))

__all__ = [
    "SOURCE_NAME",
    "JETSTREAM_URLS",
    "JETSTREAM_INDEX",
    "RECONNECT_DELAY_SECONDS",
    "MAX_RECONNECT_DELAY_SECONDS",
    "RECONNECT_BACKOFF_MULTIPLIER",
    "MAX_RECONNECT_ATTEMPTS_BEFORE_SWITCH"
]
