# saves processed trend snapshots to local JSON

import json
from datetime import datetime, timezone
from pathlib import Path

from services.storage.config import TREND_EXAMPLE_POSTS_PATH, TREND_SNAPSHOT_PATH


class TrendStore:
    def __init__(
        self,
        trend_path=TREND_SNAPSHOT_PATH,
        example_posts_path=TREND_EXAMPLE_POSTS_PATH,
    ):
        self.path = Path(trend_path)
        self.example_posts_path = Path(example_posts_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.example_posts_path.parent.mkdir(parents=True, exist_ok=True)

    def save_snapshot(self, posts_processed: int, trends: list):
        snapshot = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "posts_processed": posts_processed,
            "trends": [
                {
                    "term": term,
                    "count": count,
                }
                for term, count in trends
            ],
        }

        snapshots = self._load_snapshots()
        snapshots.append(snapshot)

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(snapshots, f, indent=2)

        print(f"Saved trend snapshot to {self.path}")

    def save_example_posts(self, posts_processed: int, examples: list):
        snapshot = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "posts_processed": posts_processed,
            "examples": examples,
        }

        snapshots = self._load_snapshots(self.example_posts_path)
        snapshots.append(snapshot)

        with open(self.example_posts_path, "w", encoding="utf-8") as f:
            json.dump(snapshots, f, indent=2)

        print(f"Saved example posts to {self.example_posts_path}")

    def _load_snapshots(self, path=None):
        path = path or self.path

        if not path.exists():
            return []

        try:
            with open(path, "r", encoding="utf-8") as f:
                snapshots = json.load(f)

            if isinstance(snapshots, list):
                return snapshots

            return []
        except (json.JSONDecodeError, OSError):
            return []
