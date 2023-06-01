"""test user model"""
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_scoped_session
from sqlalchemy.exc import IntegrityError
from sendcloud.models import User
from sendcloud.utils import get_session
from sendcloud.utils import setup_tests


async def __add_user(username: str, session: async_scoped_session) -> None:
    user = User(username=username)
    session.add(user)
    await session.commit()


@pytest.mark.asyncio
@setup_tests()
async def test_create_user() -> None:
    """Check if user can be created with correct data"""
    session: async_scoped_session
    async with get_session() as session:
        await __add_user("test_user", session)
        stmt = text("select * from users")
        retrieved_user = (await session.execute(stmt)).one_or_none()
        assert retrieved_user is not None, "test user should be added"
        assert retrieved_user.username == "test_user", "username should be test_user"
        assert retrieved_user.pk == 1, "pk should be started from 1"


@pytest.mark.asyncio
@setup_tests()
async def test_create_user_empty_username() -> None:
    """Check if user can be added with empty username"""
    session: async_scoped_session
    async with get_session() as session:
        try:
            await __add_user("", session)
        except ValueError as error:
            assert str(error) == "username too short"


@pytest.mark.asyncio
@setup_tests()
async def test_create_user_duplicate_username() -> None:
    """Check if user can be added with duplicate username"""
    session: async_scoped_session
    async with get_session() as session:
        try:
            await __add_user("unique_username", session)
            await __add_user("unique_username", session)
        except IntegrityError:
            await session.rollback()
            stmt = text("select count(1) from users")
            assert (await session.execute(stmt)).scalar() == 1, "Only one user should had been added"
