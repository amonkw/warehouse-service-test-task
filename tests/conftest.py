import pytest_asyncio
import asyncio
from httpx import AsyncClient
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

# Импортируем Base и модели для создания/удаления таблиц
from app.db.base import Base
import app.db.models  # noqa - чтобы Base знал о моделях
from app.main import app
from app.config import settings
from app.db.session import get_session_dependency  # Импорт зависимости сессии

# Создаем тестовый движок и сессию
test_engine = create_async_engine(settings.test_database_url, poolclass=NullPool)
TestSessionFactory = async_sessionmaker(
    test_engine, expire_on_commit=False, class_=AsyncSession
)


@pytest_asyncio.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Создает event loop для сессии pytest."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """Создает и удаляет тестовые таблицы для сессии."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Предоставляет тестовую сессию для каждого теста."""
    async with TestSessionFactory() as session:
        yield session
        await session.rollback()  # Откат после каждого теста


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Предоставляет тестовый HTTP клиент."""

    # Подмена зависимости сессии БД на тестовую
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_session_dependency] = override_get_session

    async with AsyncClient(app=app, base_url="http://test") as async_client:
        yield async_client

    # Очистка подмены после теста
    del app.dependency_overrides[get_session_dependency]
