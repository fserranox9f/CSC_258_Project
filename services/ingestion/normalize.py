# --------------------------------------------------------------------------------
# Normalizes the post from a Bluesky event to a defined JSON format
#  https://github.com/bluesky-social/jetstream
#
#   -- security --
#       Full post text is not logged. 
# --------------------------------------------------------------------------------

from services.ingestion.config import *

def normalize_post(event: dict):

    commit = event.get("commit", {})            # the post was commited to their servers
    record = commit.get("record", {})           # The content of the post

    content = record.get("text")                # the content of the post
    timestamp = record.get("createdAt")         # timestamp
    author = event.get("did")                   # author
    rkey = commit.get("rkey")                   # post key

    if not content:                             # skip post with no content
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