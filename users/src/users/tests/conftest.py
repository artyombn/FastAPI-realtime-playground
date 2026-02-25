import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
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

from src.core.exceptions import UserAlreadyExistsError
from src.database.uow import UnitOfWork
from src.main import app as main_app
from src.database.base import Base
from src.database.db_helper import db_helper
from users.core.exceptions import UserAlreadyExistsError
from users.database.uow import UnitOfWork
from users.main import app as main_app
from users.database.base import Base

logger = logging.getLogger("fastapi-app")


@pytest.fixture(scope="session")
def test_database_url() -> str:
    """
    Возвращает URL базы данных для тестового engine.
    Используется для инициализации подключения в тестовой сессии.
    """

    from users.config.settings import get_test_settings

    settings = get_test_settings()
    logger.debug(f"DB_TEST_URL = {settings.test_get_db_url()}")
    return settings.test_get_db_url()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def engine(test_database_url) -> AsyncGenerator[AsyncEngine, None]:
    """
    Создаёт асинхронный engine для тестов на всю тестовую сессию.

    Перед запуском тестов создаёт все таблицы, после завершения — удаляет их и освобождает ресурсы engine.

    Для полной изоляции тестов (каждый тест = своя БД) -> scope="function"
    """

    engine = create_async_engine(test_database_url, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Предоставляет новую асинхронную сессию для каждого теста.

    После выполнения теста выполняет rollback, обеспечивая изоляцию данных между тестами.
    """

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
    """
    Тестовая реализация Unit of Work.

    Использует переданную тестовую сессию и не закрывает её после выполнения, чтобы избежать ошибок при повторном использовании в рамках одного теста.
    """

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
    """
    Подменяет unit_of_work в сервисах на тестовую реализацию.

    Оригинальный UOW закрывает сессию после выхода из контекста, что приводит к ошибкам при повторных операциях в тестах.
    """

    from users.core import services

    monkeypatch.setattr(services, "unit_of_work", _test_unit_of_work)


@pytest.fixture
def session_override(db_session: AsyncSession):
    """
    Переопределяет зависимость FastAPI get_session на тестовую сессию.

    Позволяет использовать одну и ту же сессию в интеграционных тестах через TestClient.
    """

    async def get_session_override() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    main_app.dependency_overrides[db_helper.get_session] = get_session_override
    yield
    main_app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def client(session_override) -> AsyncGenerator[AsyncClient, None]:
    """
    HTTP-клиент для интеграционных тестов FastAPI-приложения.

    Использует ASGITransport и переопределённую тестовую сессию.
    """
    transport = ASGITransport(app=main_app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test_users_app:7000/",
    ) as ac:
        yield ac
