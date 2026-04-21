import json
from pathlib import Path
from config import SAVE_SAMPLE_PATH


class SampleWriter:
    def __init__(self, max_posts=100):
        self.max_posts = max_posts
        self.posts = []

    def add_post(self, post: dict):
        self.posts.append(post)
        print(f"Captured {len(self.posts)} posts")

    def is_full(self):
        return len(self.posts) >= self.max_posts

    def save(self):
        save_path = Path(SAVE_SAMPLE_PATH)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        existing_posts = []

        if save_path.exists():
            try:
                with open(save_path, "r", encoding="utf-8") as f:
                    existing_posts = json.load(f)

                if not isinstance(existing_posts, list):
                    existing_posts = []
            except (json.JSONDecodeError, OSError):
                existing_posts = []

        combined_posts = existing_posts + self.posts

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(combined_posts, f, indent=2, ensure_ascii=False)

        print(f"Saved {len(self.posts)} new posts to {save_path}")
        print(f"Total posts in file: {len(combined_posts)}")