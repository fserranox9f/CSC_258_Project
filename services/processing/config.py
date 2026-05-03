import os


POSTS_LAP = 100  # occurence of print after reading number of post
TOP_TERMS = 20 # number of words to look at
MAX_EXAMPLES_PER_TOPIC = int(os.getenv("MAX_EXAMPLES_PER_TOPIC", "25"))
MAX_TRACKED_TOPICS = int(os.getenv("MAX_TRACKED_TOPICS", "500"))
EXCLUDED_AUTHORS = {
    "did:plc:f4z2nftgrn75h7h3wucdyzaf",
}
