from sqlalchemy.orm import declarative_base

from users.config.settings import get_settings

settings = get_settings()
DATABASE_URL = settings.get_db_url()
SYNC_DB_URL = settings.get_sync_db_url()

Base = declarative_base()
