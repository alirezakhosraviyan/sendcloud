"""test Entry model"""
from datetime import datetime
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_scoped_session
from sqlalchemy.exc import IntegrityError
from freezegun import freeze_time

from sendcloud.models import Feed, Entry, User
from sendcloud.utils import get_session
from sendcloud.utils import setup_tests


@pytest.mark.asyncio
@setup_tests()
@freeze_time("1995-02-25 8:20:20")
async def test_create_feed_without_entry() -> None:
    """Check if Feed can be created with correct data"""
    session: async_scoped_session
    async with get_session() as session:
        feed = Feed(
            title="Test Feed",
            description="Test Feed Description",
            category="Test Feed Category",
            lang="Dutch",
            link="http://testfeed.com/feeds/1",
            copyright_text="Copyright (c) 2010",
            created_at=datetime.now(),  # it should be added at database server side to avoid network delay impacts
        )

        session.add(feed)
        await session.commit()

        stmt = text("select * from feeds")
        retrieved_feed = (await session.execute(stmt)).one_or_none()
        assert retrieved_feed is not None, "feed should be added"
        assert retrieved_feed[0] == 1
        assert retrieved_feed[1] == "http://testfeed.com/feeds/1"
        assert retrieved_feed[2] == "Test Feed"
        assert retrieved_feed[3] == "Dutch"
        assert retrieved_feed[4] == "Copyright (c) 2010"
        assert retrieved_feed[5] == "Test Feed Description"
        assert retrieved_feed[6] == "Test Feed Category"
        assert str(retrieved_feed[7]) == "1995-02-25 08:20:20.000000"


@pytest.mark.asyncio
@setup_tests()
async def test_create_feed_empty_link() -> None:
    """Check if Feed can be created with empty link"""
    try:
        Feed(
            title="Test Feed",
            description="Test Feed Description",
            category="Test Feed Category",
            lang="Dutch",
            link="",
            copyright_text="Copyright (c) 2010",
        )
    except ValueError as error:
        assert str(error) == "link too short"


@pytest.mark.asyncio
@setup_tests()
async def test_create_feed_duplicate_link() -> None:
    """Check if Feed can be created with duplicate link"""
    session: async_scoped_session
    async with get_session() as session:
        feed = Feed(
            title="Test Feed",
            description="Test Feed Description",
            category="Test Feed Category",
            lang="Dutch",
            link="http://testfeed.com/feeds/1",
            copyright_text="Copyright (c) 2010",
        )

        feed2 = Feed(
            title="Test2 Feed",
            description="Test2 Feed Description",
            category="Test2 Feed Category",
            lang="Dutch",
            link="http://testfeed.com/feeds/1",
            copyright_text="Copyright (c) 2010",
        )
        try:
            session.add(feed)
            await session.commit()
            session.add(feed2)
        except IntegrityError:
            await session.rollback()
            stmt = text("select count(1) from feeds")
            assert (await session.execute(stmt)).scalar() == 1, "Only one feed should had been added"


@pytest.mark.asyncio
@setup_tests()
async def test_create_entry() -> None:
    """Check if Entry can be created with correct data"""
    session: async_scoped_session
    async with get_session() as session:
        feed = Feed(
            title="Test Feed",
            description="Test Feed Description",
            category="Test Feed Category",
            lang="Dutch",
            link="http://testfeed.com/feeds/1",
            copyright_text="Copyright (c) 2010",
        )
        session.add(feed)
        await session.commit()

        entry = Entry(
            title="Test Entry",
            description="Test Entry Description",
            link="http://testfeed.com/feeds/entry/1",
            feed_id=1,
        )
        session.add(entry)

        await session.commit()

        stmt = text("select * from entries")
        retrieved_entry = (await session.execute(stmt)).one_or_none()
        assert retrieved_entry is not None, "feed should be added"
        assert retrieved_entry[0] == 1
        assert retrieved_entry[1] == "http://testfeed.com/feeds/entry/1"
        assert retrieved_entry[2] == "Test Entry"
        assert retrieved_entry[3] == "Test Entry Description"


@pytest.mark.asyncio
@setup_tests()
async def test_create_entry_without_feed() -> None:
    """Check if Entry can be created without Feed"""
    session: async_scoped_session
    async with get_session() as session:
        entry = Entry(
            title="Test Entry",
            description="Test Entry Description",
            link="http://testfeed.com/feeds/entry/1",
            feed_id=None,
        )
        session.add(entry)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            stmt = text("select count(1) from entries")
            assert (await session.execute(stmt)).scalar() == 0, "No entries should be in the database"


@pytest.mark.asyncio
@setup_tests()
async def test_create_entry_with_wrong_foreignkey() -> None:
    """Check if Entry can be created with wrong foreignkey"""
    session: async_scoped_session
    async with get_session() as session:
        entry = Entry(
            title="Test Entry",
            description="Test Entry Description",
            link="http://testfeed.com/feeds/entry/1",
            feed_id=15,
        )
        session.add(entry)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            stmt = text("select count(1) from entries")
            assert (await session.execute(stmt)).scalar() == 0, "No entries should be in the database"


@pytest.mark.asyncio
@setup_tests()
@freeze_time("1995-02-25 8:20:20")
async def test_create_feed_for_user() -> None:
    """Check if Feed can be created for a user with correct data"""
    session: async_scoped_session
    async with get_session() as session:
        feed = Feed(
            title="Test Feed",
            description="Test Feed Description",
            category="Test Feed Category",
            lang="Dutch",
            link="http://testfeed.com/feeds/1",
            copyright_text="Copyright (c) 2010",
            created_at=datetime.now(),  # it should be added at database server side to avoid network delay impacts
        )

        session.add(feed)

        await session.commit()

        user = User(username="test_user")
        user.followed_feeds.append(feed)

        session.add(user)
        await session.commit()

        stmt = text("select * from user_feed")
        retrieved_user_feed = (await session.execute(stmt)).one_or_none()

        assert retrieved_user_feed is not None, "The relationship between user and feed should exist"
        assert retrieved_user_feed.tuple() == (1, 1)


@pytest.mark.asyncio
@setup_tests()
@freeze_time("1995-02-25 8:20:20")
async def test_read_entity_by_user() -> None:
    """Check if an entity can be read by a user"""
    session: async_scoped_session
    async with get_session() as session:
        feed = Feed(
            title="Test Feed",
            description="Test Feed Description",
            category="Test Feed Category",
            lang="Dutch",
            link="http://testfeed.com/feeds/1",
            copyright_text="Copyright (c) 2010",
            created_at=datetime.now(),  # it should be added at database server side to avoid network delay impacts
        )

        session.add(feed)

        await session.commit()

        user = User(username="test_user")
        session.add(user)
        await session.commit()

        entry = Entry(
            title="Test Entry",
            description="Test Entry Description",
            link="http://testfeed.com/feeds/entry/1",
            feed_id=1,
        )
        entry.read_by.append(user)
        session.add(entry)

        await session.commit()

        stmt = text("select * from read_entries")
        retrieved_user_feed = (await session.execute(stmt)).one_or_none()

        assert retrieved_user_feed is not None, "The entry should had been saved as read"
        assert retrieved_user_feed.tuple() == (1, 1)


@pytest.mark.asyncio
@setup_tests()
@freeze_time("1995-02-25 8:20:20")
async def test_read_entity_twice() -> None:
    """Check if an entity can be read twice by a user"""
    session: async_scoped_session
    async with get_session() as session:
        feed = Feed(
            title="Test Feed",
            description="Test Feed Description",
            category="Test Feed Category",
            lang="Dutch",
            link="http://testfeed.com/feeds/1",
            copyright_text="Copyright (c) 2010",
            created_at=datetime.now(),  # it should be added at database server side to avoid network delay impacts
        )

        session.add(feed)

        await session.commit()

        user = User(username="test_user")
        session.add(user)
        await session.commit()

        entry = Entry(
            title="Test Entry",
            description="Test Entry Description",
            link="http://testfeed.com/feeds/entry/1",
            feed_id=1,
        )
        entry.read_by.append(user)
        session.add(entry)
        await session.commit()

        try:
            insert_duplicate_stmt = text("insert into read_entries (user_pk, entry_pk) values (1,1)")
            await session.execute(insert_duplicate_stmt)
            await session.commit()
        except IntegrityError:
            await session.rollback()
            stmt = text("select count(*) from read_entries")
            retrieved_user_feed = (await session.execute(stmt)).scalar()
            assert retrieved_user_feed == 1
