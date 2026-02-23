import logging
from logging.handlers import TimedRotatingFileHandler

from src.config.paths import SRC_USERS_DIR
from src.config.settings import get_settings, get_test_settings


def _resolve_is_testing() -> bool:
    """
    Определяет режим запуска:
    - Если есть .env → берём IS_TESTING оттуда
    - Если есть .env.test → берём IS_TESTING оттуда
    - Если чего-то нет — используются дефолты
    """

    main_settings = get_settings()
    test_settings = get_test_settings()

    # Если существует файл .env - значение из .env, иначе True
    is_testing_main = getattr(main_settings, "IS_TESTING", True)

    # Если существует файл .env.test - значение из .env.test, иначе False
    is_testing_test = getattr(test_settings, "IS_TESTING", False)

    use_file_logging = not (is_testing_main and is_testing_test)

    return not use_file_logging  # True = testing mode


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("fastapi-app")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    is_testing = _resolve_is_testing()

    if is_testing:
        # Тестовый режим → только stdout
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        # Прод/локальный режим → файл + stdout
        LOG_DIR = SRC_USERS_DIR / "logs"
        LOG_DIR.mkdir(parents=True, exist_ok=True)

        LOG_FILE = LOG_DIR / "app_local.log"

        file_handler = TimedRotatingFileHandler(
            LOG_FILE,
            when="midnight",
            interval=1,
            backupCount=2,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger
