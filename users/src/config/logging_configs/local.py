import logging
import os
from logging.handlers import TimedRotatingFileHandler

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "app_local.log")

handler = TimedRotatingFileHandler(
    LOG_FILE, when="midnight", interval=1, backupCount=2, encoding="utf-8"
)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

logging.basicConfig(level=logging.INFO, handlers=[handler, logging.StreamHandler()])

logger = logging.getLogger("fastapi-app")
