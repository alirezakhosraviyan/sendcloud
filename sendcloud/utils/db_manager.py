"""
db manager module which includes all database related functions like creating session, engine and update database tables
for tests goals
"""
import enum
from typing import Optional, Generator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    async_scoped_session,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from .settings import settings

Base = declarative_base()


class EDatabaseManipulationType(enum.Enum):
    """
    EMessageType
    """

    CREATE = "create_all"
    DROP = "drop_all"


def get_db_engine(database_url: Optional[str] = None) -> AsyncEngine:
    """
    Creates async engine for a given database url
    :param database_url: the database config url
    :return: async database engine
    """
    return create_async_engine(
        database_url or settings.database_url,
        echo=False,
        future=True,
    )


@asynccontextmanager
async def get_session(engine: Optional[AsyncEngine] = None) -> "AsyncGenerator[async_scoped_session]":  # type: ignore
    """
    Creates async session for a given engine
    :arg engine
    :returns AsyncSession
    """
    if engine is None:
        engine = get_db_engine(settings.database_url)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session


def get_session_injector() -> Generator[AsyncSession, None, None]:
    """
    Returns a session for fastapi to inject into routers
    :return: async database session
    """
    engine = get_db_engine(settings.database_url)
    async_session = async_sessionmaker(engine, class_=AsyncSession)
    yield async_session()


async def update_async_database_tables(mode: EDatabaseManipulationType) -> None:
    """
    Function used to create tables in async mode
    :param mode: mode, whether to create or delete a table
    :return:
    """
    engine = get_db_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(getattr(Base.metadata, str(mode.value)))
