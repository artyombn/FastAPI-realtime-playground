import logging
import os
from functools import lru_cache

from dotenv import dotenv_values
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config.paths import BASE_DIR

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Settings(BaseSettings):
    DOCKER: bool = False
    IS_TESTING: bool
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
                f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST_DOCKER}:{self.DB_PORT}/{self.DB_NAME}"
            )
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST_LOCAL}:{self.DB_PORT}/{self.DB_NAME}"
        )

    def get_sync_db_url(self) -> str:
        if self.DOCKER:
            return (
                f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST_DOCKER}:{self.DB_PORT}/{self.DB_NAME}"
            )
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST_LOCAL}:{self.DB_PORT}/{self.DB_NAME}"
        )


class TestSettings(BaseSettings):
    DOCKER: bool = False
    IS_TESTING: bool
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST_LOCAL: str
    DB_HOST_DOCKER: str
    DB_PORT: int
    DB_NAME: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env.test"),
        extra="allow",
    )

    def test_get_db_url(self) -> str:
        if self.DOCKER:
            return (
                f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST_DOCKER}:5432/{self.DB_NAME}"
            )
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST_LOCAL}:{self.DB_PORT}/{self.DB_NAME}"
        )


@lru_cache
def get_settings() -> Settings | None:
    try:
        return Settings()
    except ValidationError:
        return None


@lru_cache
def get_test_settings() -> TestSettings | None:
    try:
        env_vars = dotenv_values(os.path.join(BASE_DIR, ".env.test"))
        return TestSettings(**env_vars)
    except ValidationError:
        return None
