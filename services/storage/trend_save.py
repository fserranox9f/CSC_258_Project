# saves processed trend snapshots to local JSON

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from services.logging_utils import get_logger
from services.storage.config import TREND_EXAMPLE_POSTS_PATH, TREND_SNAPSHOT_PATH


logger = get_logger("services.storage.trend_save")


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

        self._write_json_atomic(self.path, snapshots)

        logger.info("Saved trend snapshot to %s", self.path)

    def save_example_posts(self, posts_processed: int, examples: list):
        snapshot = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "posts_processed": posts_processed,
            "examples": examples,
        }

        snapshots = self._load_snapshots(self.example_posts_path)
        snapshots.append(snapshot)

        self._write_json_atomic(self.example_posts_path, snapshots)

        logger.info("Saved example posts to %s", self.example_posts_path)

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

    def _write_json_atomic(self, path: Path, payload: list):
        path.parent.mkdir(parents=True, exist_ok=True)

        fd, temp_path = tempfile.mkstemp(
            dir=path.parent,
            prefix=f"{path.stem}.",
            suffix=".tmp",
            text=True,
        )

        try:
            with os.fdopen(fd, "w", encoding="utf-8") as temp_file:
                json.dump(payload, temp_file, indent=2)
                temp_file.flush()
                os.fsync(temp_file.fileno())

            os.replace(temp_path, path)
        except OSError:
            try:
                os.remove(temp_path)
            except OSError:
                pass

            raise
