import unittest
from pathlib import Path
from unittest.mock import patch

from services.storage.trend_save import TrendStore


class TrendStoreTests(unittest.TestCase):
    def test_save_snapshot_builds_expected_payload(self):
        store = TrendStore(
            trend_path=Path("unused-trends.json"),
            example_posts_path=Path("unused-examples.json"),
        )

        with patch.object(store, "_load_snapshots", return_value=[]), patch.object(
            store, "_write_json_atomic"
        ) as write_mock:
            store.save_snapshot(10, [("openai", 3), ("testing", 2)])

        written_path, payload = write_mock.call_args[0]

        self.assertEqual(written_path, store.path)
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["posts_processed"], 10)
        self.assertEqual(payload[0]["trends"][0], {"term": "openai", "count": 3})

    def test_save_example_posts_builds_expected_payload(self):
        store = TrendStore(
            trend_path=Path("unused-trends.json"),
            example_posts_path=Path("unused-examples.json"),
        )

        examples = [
            {
                "term": "openai",
                "count": 3,
                "example_post": {
                    "post_id": "post-1",
                    "author": "did:plc:author1",
                    "timestamp": "2026-05-03T12:00:00Z",
                    "text": "OpenAI test post",
                },
            }
        ]

        with patch.object(store, "_load_snapshots", return_value=[]), patch.object(
            store, "_write_json_atomic"
        ) as write_mock:
            store.save_example_posts(10, examples)

        written_path, payload = write_mock.call_args[0]

        self.assertEqual(written_path, store.example_posts_path)
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["posts_processed"], 10)
        self.assertEqual(payload[0]["examples"][0]["term"], "openai")


if __name__ == "__main__":
    unittest.main()
