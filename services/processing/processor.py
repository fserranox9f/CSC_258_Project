# -----------------------------------------------------
# Extracts live trends from normalized social posts.
#
#   -- Open Design --
#   The processor only works with the normalized post shape created by ingestion.
#   It does not know about Bluesky raw events or Kafka message details.
#
#   -- Scalability --
#   Topic counts and example posts are bounded so memory does not grow forever
#   as the stream continues running.
#
#   -- Fault Tolerance --
#   Invalid or unusable posts are skipped instead of crashing the service.
#
#   -- Transparency --
#   The processor tracks skipped posts and pruned topics so the main service
#   can log what happened during shutdown.
#
#   -- Security / Privacy --
#   Post text is treated as data only. Example posts are stored for the dashboard,
#   so saved snapshots may contain user-generated text.
# -----------------------------------------------------

import random
import re
from collections import Counter, deque

from services.processing.config import (
    EXCLUDED_AUTHORS,
    MAX_EXAMPLES_PER_TOPIC,
    MAX_TRACKED_TOPICS,
    STOPWORDS
)


URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
HASHTAG_PATTERN = re.compile(r"#[a-zA-Z][a-zA-Z0-9_]{2,}")
WORD_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9_]{2,}")


class TrendProcessor:
    def __init__(self):
        # Count how often each extracted trend topic appears.
        self.topic_counts = Counter()

        # Store a small bounded set of example posts for each topic.
        self.topic_examples = {}

        # Runtime counters used for logging and snapshot timing.
        self.posts_processed = 0
        self.invalid_posts_skipped = 0
        self.pruned_topics = 0

    def process_post(self, post: dict):
        # Validate the normalized post contract before using it.
        if not self._is_valid_post(post):
            self.invalid_posts_skipped += 1
            return False

        # Skip authors that should not affect trend results.
        if post.get("author") in EXCLUDED_AUTHORS:
            return False

        text = post.get("text", "")
        if not text:
            return False

        topics = self._extract_topics(text)

        # If no meaningful topics were extracted, this post does not affect trends.
        if not topics:
            return False

        # Update trend counts for every word, hashtag, or phrase found in the post.
        self.topic_counts.update(topics)

        for topic in topics:
            if topic not in self.topic_examples:
                self.topic_examples[topic] = deque(maxlen=MAX_EXAMPLES_PER_TOPIC)

            # Keep bounded examples so the dashboard can show context for a trend.
            self.topic_examples[topic].append(
                {
                    "post_id": post.get("post_id"),
                    "author": post.get("author"),
                    "timestamp": post.get("timestamp"),
                    "text": text,
                }
            )

        self._prune_tracked_topics()
        self.posts_processed += 1
        return True

    def top_terms(self, limit=10):
        # Return the most common trend topics seen so far.
        return self.topic_counts.most_common(limit)

    def top_examples(self, limit=10):
        # Pick one stored example post for each top trend.
        examples = []

        for term, count in self.top_terms(limit=limit):
            topic_posts = self.topic_examples.get(term, [])
            example_post = random.choice(topic_posts) if topic_posts else None

            examples.append(
                {
                    "term": term,
                    "count": count,
                    "example_post": example_post,
                }
            )

        return examples

    def _extract_topics(self, text: str):
        # Normalize text before extracting topics.
        text = text.lower()
        text = URL_PATTERN.sub("", text)

        # Hashtags are kept as their own trend signals.
        hashtags = HASHTAG_PATTERN.findall(text)

        # Regular words are extracted separately, then filtered through stopwords.
        words = WORD_PATTERN.findall(text)
        meaningful_words = [word for word in words if word not in STOPWORDS]
        phrases = self._build_phrases(meaningful_words)

        return hashtags + meaningful_words + phrases

    def _build_phrases(self, words: list):
        # Build simple two-word phrases to catch trends like "machine learning".
        phrases = []

        for index in range(len(words) - 1):
            first_word = words[index]
            second_word = words[index + 1]
            phrases.append(f"{first_word} {second_word}")

        return phrases

    def _prune_tracked_topics(self):
        # Keep only the most common topics so long-running streams stay bounded.
        overflow = len(self.topic_counts) - MAX_TRACKED_TOPICS
        if overflow <= 0:
            return

        for topic, _count in self.topic_counts.most_common()[MAX_TRACKED_TOPICS:]:
            self.topic_counts.pop(topic, None)
            self.topic_examples.pop(topic, None)
            self.pruned_topics += 1

    def _is_valid_post(self, post):
        # Validate the normalized post schema expected from ingestion.
        if not isinstance(post, dict):
            return False

        required_string_fields = ("post_id", "text", "author", "source")
        for field in required_string_fields:
            value = post.get(field)
            if not isinstance(value, str) or not value.strip():
                return False

        timestamp = post.get("timestamp")
        is_repost = post.get("is_repost")

        if timestamp is not None and not isinstance(timestamp, str):
            return False

        if not isinstance(is_repost, bool):
            return False

        return True
