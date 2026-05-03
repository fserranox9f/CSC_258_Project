import os
from pathlib import Path


def find_base_dir() -> Path:
    current_file = Path(__file__).resolve()

    for parent in current_file.parents:
        if (parent / "services").exists() or (parent / "storage").exists():
            return parent

    return current_file.parents[1]


BASE_DIR = Path(os.getenv("PROJECT_ROOT", find_base_dir()))
TREND_DATA_PATH = Path(
    os.getenv(
        "TREND_DATA_PATH",
        str(BASE_DIR / "storage" / "data" / "sample_post.json"),
    )
)

WINDOW_SIZE = int(os.getenv("TREND_WINDOW_SIZE", "1000"))
TOP_K_TRENDS = int(os.getenv("TREND_TOP_K", "5"))
TREND_TERM_MODE = os.getenv("TREND_TERM_MODE", "auto").lower()
TREND_SOURCE_FILTER = os.getenv("TREND_SOURCE_FILTER", "").strip().lower() or None
SEED_LIVE_FROM_FILE = os.getenv("TREND_SEED_LIVE_FROM_FILE", "true").lower() == "true"
APP_HOST = os.getenv("TREND_SERVICE_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("TREND_SERVICE_PORT", "5000"))
APP_DEBUG = os.getenv("TREND_SERVICE_DEBUG", "true").lower() == "true"
