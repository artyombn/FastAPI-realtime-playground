from contextlib import asynccontextmanager

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import UserAlreadyExistsError


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    async def close(self):
        await self.session.close()


@asynccontextmanager
async def unit_of_work(session: AsyncSession):
    uow = UnitOfWork(session)
    try:
        yield uow
        await uow.commit()
    except IntegrityError as e:
        await uow.rollback()
        raise UserAlreadyExistsError() from e
    except SQLAlchemyError:
        await uow.rollback()
        raise
    finally:
        await uow.close()
