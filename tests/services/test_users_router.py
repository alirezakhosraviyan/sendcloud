"""test user services"""
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_scoped_session
from fastapi.exceptions import HTTPException


from sendcloud.utils import get_session
from sendcloud.utils import setup_tests
from sendcloud.models import User, Feed
from sendcloud.services import users_services as user_services


async def __add_user_wit_feed(username: str, feed_link: str, session: async_scoped_session) -> None:
    feed = Feed(
        title="Test title",
        description="Test Feed Description",
        category="Test Feed Category",
        lang="Dutch",
        link=feed_link,
        copyright_text="Copyright (c) 2010",
    )
    session.add(feed)
    await session.commit()

    user = User(username=username)
    session.add(user)
    user.followed_feeds.append(feed)
    await session.commit()


@pytest.mark.asyncio
@setup_tests()
async def test_get_users() -> None:
    """Check if all users can be retrieved"""
    session: async_scoped_session
    async with get_session() as session:
        await __add_user_wit_feed("test_user1", "http://testfeed.com/feeds/1", session)
        await __add_user_wit_feed("test_user2", "http://testfeed.com/feeds/2", session)

        users = await user_services.get_users(session)
        assert len(users) == 2
        assert users[0].username == "test_user1"
        assert users[1].username == "test_user2"
        assert users[0].followed_feeds[0].link == "http://testfeed.com/feeds/1"
        assert users[1].followed_feeds[0].link == "http://testfeed.com/feeds/2"


@pytest.mark.asyncio
@setup_tests()
async def test_get_user() -> None:
    """Check if a user can be retrieved with the username"""
    session: async_scoped_session
    async with get_session() as session:
        await __add_user_wit_feed("test_user1", "http://testfeed.com/feeds/1", session)
        await __add_user_wit_feed("test_user2", "http://testfeed.com/feeds/2", session)

        user = await user_services.get_user_by_username("test_user1", session)
        assert user is not None
        assert user.username == "test_user1"


@pytest.mark.asyncio
@setup_tests()
async def test_get_user_which_doesnt_exist() -> None:
    """Check if a user can be retrieved with an invalid username"""
    session: async_scoped_session
    async with get_session() as session:
        await __add_user_wit_feed("test_user1", "http://testfeed.com/feeds/1", session)

        user = await user_services.get_user_by_username("test_user3", session)
        assert user is None


@pytest.mark.asyncio
@setup_tests()
async def test_create_user() -> None:
    """Check if a user can be created with correct data"""
    session: async_scoped_session
    async with get_session() as session:
        await user_services.create_user("test_user1", session)

        user_stmt = text("select * from users")
        user = (await session.execute(user_stmt)).one_or_none()

        assert user is not None
        assert user.username == "test_user1"


@pytest.mark.asyncio
@setup_tests()
async def test_create_duplicate_user() -> None:
    """Check if a user can be created with correct data"""
    session: async_scoped_session
    async with get_session() as session:
        try:
            await user_services.create_user("test_user1", session)
            await user_services.create_user("test_user1", session)
        except HTTPException:
            await session.rollback()
            user_stmt = text("select count(1) from users")
            user_counts = (await session.execute(user_stmt)).scalar()
            assert user_counts == 1
