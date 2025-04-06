import logging
from asyncio import current_task
from contextlib import asynccontextmanager
from urllib.parse import urlparse, urlunparse

from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, async_scoped_session

from app.config import settings

logger = logging.getLogger("warehouse-service:db")

# Конфигурация движка
engine = create_async_engine(
    settings.database_url,
    echo=settings.ECHO_SQL,
    poolclass=NullPool if settings.IS_AUTOTEST else None,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10
)

# Базовый sessionmaker для всех типов сессий
base_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession
)


@asynccontextmanager
async def get_session():
    """
    Сессия для API (FastAPI Depends)
    - Автоматическое управление транзакциями
    - Гарантированное закрытие соединения
    """
    async with base_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"API session rollback: {str(e)}", exc_info=True)
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_scoped_session():
    """
    Scoped сессия для фоновых задач (Kafka consumer и др.)
    - Привязка к текущей asyncio task
    - Долгоживущие соединения
    """
    scoped_factory = async_scoped_session(
        base_session_factory,
        scopefunc=current_task
    )
    try:
        async with scoped_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Background task session rollback: {str(e)}", exc_info=True)
                raise
    finally:
        await scoped_factory.remove()


async def create_db_async():
    """Создание БД при инициализации (без изменений)"""
    parsed = list(urlparse(settings.database_url))
    db_name = parsed[2].lstrip("/").split("?")[0]

    if not db_name:
        raise ValueError("Database name not found in URL")

    parsed[2] = "/postgres"
    admin_url = urlunparse(parsed)

    admin_engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
    async with admin_engine.connect() as conn:
        try:
            result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": db_name}
            )
            if not result.scalar_one_or_none():
                await conn.execute(text(f"CREATE DATABASE {db_name}"))
        except Exception as e:
            logger.exception(f"Database creation failed: {str(e)}")
            raise
        finally:
            await admin_engine.dispose()

async def get_session_dependency() -> AsyncSession:
    """
    Функция для использования в FastAPI Depends
    Возвращает сессию без контекстного менеджера
    """
    session = base_session_factory()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"API session rollback: {str(e)}", exc_info=True)
        raise
    finally:
        await session.close()