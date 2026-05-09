# --------------------------------------------------------------------------------
# Normalizes the post from a Bluesky event to a defined JSON format
#  https://github.com/bluesky-social/jetstream
#
# --------------------------------------------------------------------------------

from services.ingestion.config import SOURCE_NAME


def normalize_post(event: dict):
    commit = event.get("commit", {})
    record = commit.get("record", {})

    content = record.get("text")
    timestamp = record.get("createdAt")
    author = event.get("did")
    rkey = commit.get("rkey")

    if not content:
        return None

    post_id = f"{author}:{rkey}" if author and rkey else author or "unknown"

    return {
        "post_id": post_id,
        "timestamp": timestamp,
        "text": content,
        "author": author,
        "source": SOURCE_NAME,
        "is_repost": False,
    }
