from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
BASE_DIR = PROJECT_DIR / "users"

SRC_USERS_DIR = BASE_DIR / "src/users"
MEDIA_USERS_DIR: Path = SRC_USERS_DIR / "media"
MEDIA_USERS_DIR.mkdir(parents=True, exist_ok=True)
