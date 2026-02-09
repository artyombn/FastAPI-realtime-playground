from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # src/
MEDIA_DIR = BASE_DIR / "media"

MEDIA_DIR.mkdir(parents=True, exist_ok=True)
