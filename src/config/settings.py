import logging
import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = BASE_DIR / "src"
MEDIA_DIR = SRC_DIR / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

log = logging.getLogger(__name__)


class Settings(BaseSettings):
    DOCKER: bool = True
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST_LOCAL: str
    DB_HOST_DOCKER: str
    DB_PORT: int
    DB_NAME: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        extra="allow",
    )

    @staticmethod
    def configure_logging(level: int = logging.INFO) -> None:
        logging.basicConfig(
            level=level,
            datefmt="%Y-%m-%d %H:%M:%S",
            format="[%(asctime)s.%(msecs)03d] "
            "%(funcName)20s "
            "%(module)s:%(lineno)d "
            "%(levelname)-8s - "
            "%(message)s",
        )

    def get_db_url(self) -> str:
        if self.DOCKER:
            return (
                f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST_DOCKER}:{self.DB_PORT}/{self.DB_NAME}"
            )
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST_LOCAL}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
