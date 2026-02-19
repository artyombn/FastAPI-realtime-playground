from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = BASE_DIR / "src"
MEDIA_DIR: Path = SRC_DIR / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
