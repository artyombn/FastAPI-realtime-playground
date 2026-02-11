from contextlib import contextmanager

from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from src.database.exceptions import UnitOfWorkError
from src.database.base import SessionLocal


class UnitOfWork:
    def __init__(self):
        self.session = SessionLocal()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def close(self):
        self.session.close()


@contextmanager
def unit_of_work():
    uow = UnitOfWork()
    try:
        yield uow
        uow.commit()
    except (SQLAlchemyError, IntegrityError) as e:
        uow.rollback()
        raise UnitOfWorkError() from e
    finally:
        uow.close()
