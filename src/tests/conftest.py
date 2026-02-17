from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from src.core.user.exceptions import UserAlreadyExistsError
from src.database.uow import UnitOfWork
from src.main import app as main_app
from src.database.base import Base
from src.database.db_helper import db_helper


@pytest.fixture(scope="session")
def app_database_url() -> str:
    from src.config.settings import get_settings

    settings = get_settings()
    return settings.get_db_url()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def engine(app_database_url) -> AsyncGenerator[AsyncEngine, None]:
    """Создаёт тестовый engine один раз для всех тестов"""
    engine = create_async_engine(app_database_url, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    async with factory() as session:
        yield session
        await session.rollback()


@asynccontextmanager
async def _test_unit_of_work(db_session: AsyncSession):
    uow = UnitOfWork(db_session)
    try:
        yield uow
        await uow.commit()
    except IntegrityError as e:
        await uow.rollback()
        raise UserAlreadyExistsError() from e
    except SQLAlchemyError:
        await uow.rollback()
        raise


@pytest.fixture
def patch_uow(monkeypatch):
    from src.core.user import services

    monkeypatch.setattr(services, "unit_of_work", _test_unit_of_work)


@pytest.fixture
def session_override(db_session: AsyncSession):
    async def get_session_override() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    main_app.dependency_overrides[db_helper.get_session] = get_session_override
    yield
    main_app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def client(session_override) -> AsyncGenerator[AsyncClient, None]:
    """
    HTTP клиент для интеграционных тестов.
    """
    transport = ASGITransport(app=main_app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as ac:
        yield ac
