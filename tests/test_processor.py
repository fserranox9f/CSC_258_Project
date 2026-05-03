import unittest
from unittest.mock import patch

from services.processing.processor import TrendProcessor


class TrendProcessorTests(unittest.TestCase):
    def setUp(self):
        self.processor = TrendProcessor()

    def test_process_post_counts_terms_and_phrases(self):
        post = {
            "post_id": "post-1",
            "timestamp": "2026-05-03T12:00:00Z",
            "text": "OpenAI builds #Testing systems",
            "author": "did:plc:author1",
            "source": "bluesky",
            "is_repost": False,
        }

        processed = self.processor.process_post(post)

        self.assertTrue(processed)
        self.assertEqual(self.processor.posts_processed, 1)
        self.assertIn("#testing", self.processor.topic_counts)
        self.assertIn("openai", self.processor.topic_counts)
        self.assertIn("builds", self.processor.topic_counts)
        self.assertIn("systems", self.processor.topic_counts)
        self.assertIn("openai builds", self.processor.topic_counts)

    def test_process_post_rejects_invalid_payload(self):
        invalid_post = {
            "post_id": "",
            "timestamp": "2026-05-03T12:00:00Z",
            "text": "Hello world",
            "author": "did:plc:author1",
            "source": "bluesky",
            "is_repost": False,
        }

        processed = self.processor.process_post(invalid_post)

        self.assertFalse(processed)
        self.assertEqual(self.processor.invalid_posts_skipped, 1)
        self.assertEqual(self.processor.posts_processed, 0)

    def test_examples_per_topic_are_bounded(self):
        with patch("services.processing.processor.MAX_EXAMPLES_PER_TOPIC", 2):
            processor = TrendProcessor()

            for index in range(3):
                processor.process_post(
                    {
                        "post_id": f"post-{index}",
                        "timestamp": "2026-05-03T12:00:00Z",
                        "text": "OpenAI systems",
                        "author": f"did:plc:author{index}",
                        "source": "bluesky",
                        "is_repost": False,
                    }
                )

        self.assertEqual(len(processor.topic_examples["openai"]), 2)

    def test_tracked_topics_are_pruned_when_limit_is_exceeded(self):
        with patch("services.processing.processor.MAX_TRACKED_TOPICS", 2):
            processor = TrendProcessor()

            processor.topic_counts.update({"topic-a": 5, "topic-b": 4, "topic-c": 1})
            processor.topic_examples = {
                "topic-a": [],
                "topic-b": [],
                "topic-c": [],
            }

            processor._prune_tracked_topics()

        self.assertIn("topic-a", processor.topic_counts)
        self.assertIn("topic-b", processor.topic_counts)
        self.assertNotIn("topic-c", processor.topic_counts)
        self.assertEqual(processor.pruned_topics, 1)


if __name__ == "__main__":
    unittest.main()
