from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

SRC_USERS_DIR = BASE_DIR / "users/src"
MEDIA_USERS_DIR: Path = SRC_USERS_DIR / "media"
MEDIA_USERS_DIR.mkdir(parents=True, exist_ok=True)
