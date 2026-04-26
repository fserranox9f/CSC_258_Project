# extracts simple live trends from normalized social posts

import random
import re
from collections import Counter
from services.storage.logs.unwanted_words import STOPWORDS

URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
HASHTAG_PATTERN = re.compile(r"#[a-zA-Z][a-zA-Z0-9_]{2,}")
WORD_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9_]{2,}")


class TrendProcessor:
    def __init__(self):
        self.topic_counts = Counter()
        self.topic_examples = {}
        self.posts_processed = 0

    def process_post(self, post: dict):
        text = post.get("text", "")

        if not text:
            return

        topics = self._extract_topics(text)

        if not topics:
            return

        self.topic_counts.update(topics)

        for topic in topics:
            if topic not in self.topic_examples:
                self.topic_examples[topic] = []

            self.topic_examples[topic].append(
                {
                    "post_id": post.get("post_id"),
                    "author": post.get("author"),
                    "timestamp": post.get("timestamp"),
                    "text": text,
                }
            )

        self.posts_processed += 1

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
