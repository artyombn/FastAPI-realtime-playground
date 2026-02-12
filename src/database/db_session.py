from src.database.base import SessionLocal


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
