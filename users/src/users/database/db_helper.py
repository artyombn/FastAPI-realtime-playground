from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class DatabaseHelper:
    """Менеджер подключения к бд."""

    def __init__(self, db_url: str, echo: bool = False) -> None:
        """Инициализирует асинхронный engine и создает фабрику сессий."""

        self.engine: AsyncEngine = create_async_engine(url=db_url, echo=echo)
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Получение асинхронной сессии."""
        async with self.session_factory() as session:
            yield session

    async def dispose(self) -> None:
        """Утилизация Engine при завершении работы приложения."""
        await self.engine.dispose()


settings = get_settings()
db_helper = DatabaseHelper(db_url=settings.get_db_url(), echo=False)
