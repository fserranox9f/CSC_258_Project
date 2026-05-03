# extracts simple live trends from normalized social posts

import random
import re
from collections import Counter, deque
from services.processing.config import (
    EXCLUDED_AUTHORS,
    MAX_EXAMPLES_PER_TOPIC,
    MAX_TRACKED_TOPICS,
)
from services.storage.logs.unwanted_words import STOPWORDS

URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
HASHTAG_PATTERN = re.compile(r"#[a-zA-Z][a-zA-Z0-9_]{2,}")
WORD_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9_]{2,}")


class TrendProcessor:
    def __init__(self):
        self.topic_counts = Counter()
        self.topic_examples = {}
        self.posts_processed = 0
        self.invalid_posts_skipped = 0
        self.pruned_topics = 0

    def process_post(self, post: dict):
        if not self._is_valid_post(post):
            self.invalid_posts_skipped += 1
            return False

        if post.get("author") in EXCLUDED_AUTHORS:
            return False

        text = post.get("text", "")

        if not text:
            return False

        topics = self._extract_topics(text)

        if not topics:
            return False

        self.topic_counts.update(topics)

        for topic in topics:
            if topic not in self.topic_examples:
                self.topic_examples[topic] = deque(maxlen=MAX_EXAMPLES_PER_TOPIC)

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
        return self.topic_counts.most_common(limit)

    def top_examples(self, limit=10):
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
        text = text.lower()
        text = URL_PATTERN.sub("", text)

        hashtags = HASHTAG_PATTERN.findall(text)
        words = WORD_PATTERN.findall(text)

        meaningful_words = [
            word
            for word in words
            if word not in STOPWORDS
        ]

        phrases = self._build_phrases(meaningful_words)

        return hashtags + meaningful_words + phrases

    def _build_phrases(self, words: list):
        phrases = []

        for index in range(len(words) - 1):
            first_word = words[index]
            second_word = words[index + 1]

            phrases.append(f"{first_word} {second_word}")

        return phrases

    def _prune_tracked_topics(self):
        overflow = len(self.topic_counts) - MAX_TRACKED_TOPICS

        if overflow <= 0:
            return

        for topic, _count in self.topic_counts.most_common()[MAX_TRACKED_TOPICS:]:
            self.topic_counts.pop(topic, None)
            self.topic_examples.pop(topic, None)
            self.pruned_topics += 1

    def _is_valid_post(self, post):
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
