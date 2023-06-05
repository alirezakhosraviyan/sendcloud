"""test Posting model"""
from datetime import datetime
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_scoped_session
from sqlalchemy.exc import IntegrityError
from freezegun import freeze_time

from sendcloud.models import Feed, Posting, User
from sendcloud.utils import get_session
from sendcloud.utils import setup_tests


@pytest.mark.asyncio
@setup_tests()
@freeze_time("1995-02-25 8:20:20")
async def test_create_feed_without_posting() -> None:
    """Check if Feed can be created with correct data"""
    print(33333333)
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
        print(2)
        session.add(feed)
        await session.commit()
        print(1)
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
        assert str(retrieved_feed[7]) == "1995-02-25 08:20:20"


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
async def test_create_posting() -> None:
    """Check if Posting can be created with correct data"""
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

        posting = Posting(
            title="Test Posting",
            description="Test Posting Description",
            link="http://testfeed.com/feeds/posting/1",
            author="test author",
            published_at=datetime.now(),
            feed_id=1,
        )
        session.add(posting)

        await session.commit()

        stmt = text("select * from postings")
        retrieved_posting = (await session.execute(stmt)).one_or_none()
        assert retrieved_posting is not None, "feed should be added"
        assert retrieved_posting[0] == 1
        assert retrieved_posting[1] == "http://testfeed.com/feeds/posting/1"
        assert retrieved_posting[2] == "Test Posting"
        assert retrieved_posting[3] == "Test Posting Description"


@pytest.mark.asyncio
@setup_tests()
async def test_create_posting_without_feed() -> None:
    """Check if posting can be created without Feed"""
    session: async_scoped_session
    async with get_session() as session:
        posting = Posting(
            title="Test Posting",
            description="Test Posting Description",
            link="http://testfeed.com/feeds/posting/1",
            author="test author",
            published_at=datetime.now(),
            feed_id=None,
        )
        session.add(posting)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            stmt = text("select count(1) from postings")
            assert (await session.execute(stmt)).scalar() == 0, "No postings should be in the database"


@pytest.mark.asyncio
@setup_tests()
async def test_create_posting_with_wrong_foreignkey() -> None:
    """Check if posting can be created with wrong foreignkey"""
    session: async_scoped_session
    async with get_session() as session:
        posting = Posting(
            title="Test posting",
            description="Test posting Description",
            link="http://testfeed.com/feeds/posting/1",
            author="test author",
            published_at=datetime.now(),
            feed_id=15,
        )
        session.add(posting)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            stmt = text("select count(1) from postings")
            assert (await session.execute(stmt)).scalar() == 0, "No postings should be in the database"


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
async def test_read_posting_by_user() -> None:
    """Check if a posting can be read by a user"""
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

        posting = Posting(
            title="Test Posting",
            description="Test Posting Description",
            link="http://testfeed.com/feeds/posting/1",
            author="test author",
            published_at=datetime.now(),
            feed_id=1,
        )
        posting.read_by.append(user)
        session.add(posting)

        await session.commit()

        stmt = text("select * from read_postings")
        retrieved_user_feed = (await session.execute(stmt)).one_or_none()

        assert retrieved_user_feed is not None, "The posting should had been saved as read"
        assert retrieved_user_feed.tuple() == (1, 1)


@pytest.mark.asyncio
@setup_tests()
@freeze_time("1995-02-25 8:20:20")
async def test_read_posting_twice() -> None:
    """Check if a posting can be read twice by a user"""
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

        posting = Posting(
            title="Test posting",
            description="Test posting Description",
            link="http://testfeed.com/feeds/posting/1",
            author="test author",
            published_at=datetime.now(),
            feed_id=1,
        )
        posting.read_by.append(user)
        session.add(posting)
        await session.commit()

        try:
            insert_duplicate_stmt = text("insert into read_postings (user_pk, posting_pk) values (1,1)")
            await session.execute(insert_duplicate_stmt)
        except IntegrityError:
            await session.rollback()
            stmt = text("select count(*) from read_postings")
            retrieved_user_feed = (await session.execute(stmt)).scalar()
            assert retrieved_user_feed == 1
