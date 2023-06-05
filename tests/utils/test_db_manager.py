"""test_db_manager"""
import os
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from sendcloud.utils.db_manager import (
    get_db_engine,
    get_session,
    update_async_database_tables,
    EDatabaseManipulationType,
)

DATABASE_URL = "sqlite+aiosqlite:///.sql_app.db"


@pytest.mark.asyncio
async def test_get_engine() -> None:
    """check if engine can be created for a given database"""
    engine = get_db_engine(DATABASE_URL)
    async with engine.connect() as connection:
        assert not connection.closed, "connection should be opened"
    assert connection.closed, "connection should be closed"
    os.remove(".sql_app.db")


@pytest.mark.asyncio
async def test_get_session() -> None:
    """check if session is available for a given engine"""
    session: AsyncSession
    engine = get_db_engine(DATABASE_URL)
    async with get_session(engine) as session:
        res = (await session.execute(text("select 1"))).scalar()
        assert res == 1, "result should be 1"
    os.remove(".sql_app.db")


@pytest.mark.asyncio
async def test_update_async_database_tables() -> None:
    """check if tables are being created for a given database"""
    session: AsyncSession
    await update_async_database_tables(EDatabaseManipulationType.CREATE)
    async with get_session() as session:
        res = (await session.execute(text("select count(1) from users"))).scalar()
        assert res == 0, "result should be 0"
