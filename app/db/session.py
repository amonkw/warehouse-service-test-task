import logging
from asyncio import current_task
from contextlib import asynccontextmanager
from urllib.parse import urlparse, urlunparse

from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, async_scoped_session
from app.config import settings

logger = logging.getLogger("warehouse-service:db")

engine = create_async_engine(
    settings.database_url,
    echo=settings.ECHO_SQL,
    poolclass=NullPool if settings.IS_AUTOTEST else None,
)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)

@asynccontextmanager
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session  # Автоматическое управление транзакциями в 2.0+


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False, autoflush=False)

@asynccontextmanager
async def get_scoped_session():
    scoped_factory = async_scoped_session(
        async_sessionmaker(engine, expire_on_commit=False),
        scopefunc=current_task,
    )
    try:
        async with scoped_factory() as s:
            yield s
    finally:
        await scoped_factory.remove()


async def create_db_async():
    parsed = list(urlparse(settings.database_url))
    db_name = parsed[2]
    if db_name[:1] == "/":
        db_name = db_name[1:]
    db_name = db_name.split("?", 1)[0]
    parsed[2] = ""  # path
    engine = create_async_engine(urlunparse(parsed), echo=settings.DEBUG)
    conn = await engine.connect()
    try:
        await conn.execute(text("COMMIT"))
        data = await conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        )
        if not data.scalar_one_or_none():
            await conn.execute(text(f"CREATE DATABASE {db_name}"))
        await conn.commit()
    except Exception:
        logger.exception("Can't create database")
        await conn.rollback()
    await conn.close()
    await engine.dispose()