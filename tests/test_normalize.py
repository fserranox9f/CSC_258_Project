import unittest

from services.ingestion.normalize import normalize_post


class NormalizePostTests(unittest.TestCase):
    def test_normalize_post_builds_expected_shape(self):
        event = {
            "did": "did:plc:testauthor",
            "commit": {
                "rkey": "abc123",
                "record": {
                    "text": "Hello Bluesky",
                    "createdAt": "2026-05-03T12:00:00Z",
                },
            },
        }

        normalized = normalize_post(event)

        self.assertEqual(
            normalized,
            {
                "post_id": "did:plc:testauthor:abc123",
                "timestamp": "2026-05-03T12:00:00Z",
                "text": "Hello Bluesky",
                "author": "did:plc:testauthor",
                "source": "bluesky",
                "is_repost": False,
            },
        )

    def test_normalize_post_returns_none_for_missing_text(self):
        event = {
            "did": "did:plc:testauthor",
            "commit": {
                "rkey": "abc123",
                "record": {},
            },
        }

        self.assertIsNone(normalize_post(event))


if __name__ == "__main__":
    unittest.main()
