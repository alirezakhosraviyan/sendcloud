"""test feed services"""
import datetime
from typing import List
from unittest.mock import patch, MagicMock
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_scoped_session

from sendcloud.utils import get_session
from sendcloud.utils import setup_tests
from sendcloud.models import User, Feed, Posting
from sendcloud.schemas import FeedItemCreate, PostingItemCreate
from sendcloud.services import feeds_services as feed_services


def __create_feed_and_posting_schemas(feed_link: str, posting_links: List[str]):
    """
    create sanple data for tests
    :param feed_link:
    :param posting_links:
    :return:
    """
    feed = FeedItemCreate(
        link=feed_link,
        title="feed_title",
        lang="feed_lank",
        copyright_text="feed_copyright_test",
        description="test_description",
        category="cat1",
    )
    posting_items = [
        PostingItemCreate(
            link=cur,
            title="posting_title",
            author="posting_author",
            published_at=datetime.datetime.now(),
            description="posting_description",
        )
        for cur in posting_links
    ]
    return feed, posting_items


@pytest.mark.asyncio
@setup_tests()
async def test_get_feed_by_pk() -> None:
    """check if we retrieve feed with the given pk"""
    session: async_scoped_session
    async with get_session() as session:
        feed = Feed(
            title="Test title",
            description="Test Feed Description",
            category="Test Feed Category",
            lang="Dutch",
            link="test_link",
            copyright_text="Copyright (c) 2010",
        )
        session.add(feed)
        await session.commit()
        retrieved_feed = await feed_services.get_feed_by_pk(1, session)
        assert retrieved_feed is not None
        assert retrieved_feed[0].pk == 1
        assert retrieved_feed[0].title == "Test title"
        assert retrieved_feed[0].link == "test_link"


@pytest.mark.asyncio
@setup_tests()
async def test_get_feed_by_pk_with_wrong_pk() -> None:
    """check if we retrieve feed with wrong pk"""
    session: async_scoped_session
    async with get_session() as session:
        feed = Feed(
            title="Test title",
            description="Test Feed Description",
            category="Test Feed Category",
            lang="Dutch",
            link="test_link",
            copyright_text="Copyright (c) 2010",
        )
        session.add(feed)
        await session.commit()
        retrieved_feed = await feed_services.get_feed_by_pk(2, session)
        assert retrieved_feed is None, "shouldn't return any feed"


@pytest.mark.asyncio
@setup_tests()
async def test_insert_or_update() -> None:
    """check if we can add feed with correct data"""
    session: async_scoped_session
    async with get_session() as session:
        feed, posting_items = __create_feed_and_posting_schemas("feed_link", ["posting_link1", "posting_link2"])

        feed_pk = await feed_services.insert_or_update_feed(feed, posting_items, session)
        assert feed_pk == 1

        feeds_stmt = text("select * from feeds")
        feeds = (await session.execute(feeds_stmt)).all()

        assert len(feeds) == 1
        assert feeds[0].link == "feed_link"

        postings_stmt = text("select * from postings")
        postings = (await session.execute(postings_stmt)).all()

        assert len(postings) == 2
        assert postings[0].link == "posting_link1"
        assert postings[1].link == "posting_link2"


@pytest.mark.asyncio
@setup_tests()
async def test_insert_or_update_with_duplicate_data() -> None:
    """check if we can add feed with duplicate data"""
    session: async_scoped_session
    async with get_session() as session:
        # first we make sure something is in database
        feed, posting_items = __create_feed_and_posting_schemas("feed_link", ["posting_link1", "posting_link2"])
        await feed_services.insert_or_update_feed(feed, posting_items, session)

        # then we try to add duplicate data
        feed.title = "feed title should had been changed to me!"
        posting_items[0].title = "posting 1 title should had been changed to me!"
        posting_items[1].title = "posting 2 title should had been changed to me!"
        await feed_services.insert_or_update_feed(feed, posting_items, session)

        feeds_stmt = text("select * from feeds")
        feeds = (await session.execute(feeds_stmt)).all()

        assert len(feeds) == 1
        assert feeds[0].link == "feed_link"
        assert feeds[0].title == "feed title should had been changed to me!"

        postings_stmt = text("select * from postings")
        postings = (await session.execute(postings_stmt)).all()

        assert len(postings) == 2
        assert postings[0].link == "posting_link1"
        assert postings[0].title == "posting 1 title should had been changed to me!"
        assert postings[1].link == "posting_link2"
        assert postings[1].title == "posting 2 title should had been changed to me!"


@pytest.mark.asyncio
@patch(
    "sendcloud.services.feeds_services.fetch_feed",
    return_value=__create_feed_and_posting_schemas("test_feed_link1", ["posting_link1"]),
)
@setup_tests()
async def test_follow_new_feed_which_doesnt_exist(feed_fetch_mock: MagicMock) -> None:
    """check if we can follow new feed which doesn't exist with correct data"""
    session: async_scoped_session
    async with get_session() as session:
        user = User(username="test_username")
        session.add(user)
        await session.commit()

        await feed_services.follow_new_feed("test_username", "test_feed_link1", session)

        feed_fetch_mock.assert_called_with("test_feed_link1")

        feeds_stmt = text("select * from feeds")
        feeds = (await session.execute(feeds_stmt)).all()

        assert len(feeds) == 1
        assert feeds[0].link == "test_feed_link1"

        postings_stmt = text("select * from postings")
        postings = (await session.execute(postings_stmt)).all()

        assert len(postings) == 1
        assert postings[0].link == "posting_link1"

        postings_stmt = text("select * from user_feed where user_pk=1 and feed_pk=1")
        postings = (await session.execute(postings_stmt)).all()

        assert len(postings) == 1


@pytest.mark.asyncio
@patch("sendcloud.services.feeds_services.fetch_feed")
@setup_tests()
async def test_follow_new_feed_which_already_exists(feed_fetch_mock: MagicMock) -> None:
    """check if we can follow new feed which already exists with correct data"""
    session: async_scoped_session
    async with get_session() as session:
        feed = Feed(
            title="Test title",
            description="Test Feed Description",
            category="Test Feed Category",
            lang="Dutch",
            link="test_feed_link1",
            copyright_text="Copyright (c) 2010",
        )
        session.add(feed)
        await session.commit()

        user = User(username="test_username")
        user.followed_feeds.append(feed)
        session.add(user)
        await session.commit()

        await feed_services.follow_new_feed("test_username", "test_feed_link1", session)

        feed_fetch_mock.assert_not_called()

        feeds_stmt = text("select * from feeds")
        feeds = (await session.execute(feeds_stmt)).all()

        assert len(feeds) == 1, "we shouldn't add more feeds"
        assert feeds[0].link == "test_feed_link1"

        user_feed_stmt = text("select count(*) from user_feed where user_pk=1 and feed_pk=1")
        user_feed_count = (await session.execute(user_feed_stmt)).scalar()

        assert user_feed_count == 1, "we should have added one relationship"


@pytest.mark.asyncio
@setup_tests()
async def test_follow_new_feed_when_user_doesnt_exist() -> None:
    """check to make sure we prevent following anything when user does not exist"""
    session: async_scoped_session
    async with get_session() as session:
        res = await feed_services.follow_new_feed("test_username", "test_feed_link1", session)

        assert res is None

        feeds_stmt = text("select * from feeds")
        feeds = (await session.execute(feeds_stmt)).all()

        assert len(feeds) == 0, "we shouldn't add more feeds"


@pytest.mark.asyncio
@setup_tests()
async def test_unfollow_feed_which_exists() -> None:
    """check if we can unfollow a feed which exists"""
    session: async_scoped_session
    async with get_session() as session:
        feed = Feed(
            title="Test title",
            description="Test Feed Description",
            category="Test Feed Category",
            lang="Dutch",
            link="test_feed_link1",
            copyright_text="Copyright (c) 2010",
        )
        session.add(feed)
        await session.commit()

        user = User(username="test_username")
        user.followed_feeds.append(feed)
        session.add(user)
        await session.commit()

        res = await feed_services.unfollow_feed("test_username", "test_feed_link1", session)

        assert res

        feeds_stmt = text("select * from feeds")
        feeds = (await session.execute(feeds_stmt)).all()

        assert len(feeds) == 1, "we shouldn't remove the feed"
        assert feeds[0].link == "test_feed_link1"

        user_feed_stmt = text("select count(*) from user_feed where user_pk=1 and feed_pk=1")
        user_feed_count = (await session.execute(user_feed_stmt)).scalar()

        assert user_feed_count == 0, "we just must remove relationship"


@pytest.mark.asyncio
@setup_tests()
async def test_unfollow_feed_which_doesnt_exists() -> None:
    """check if we can unfollow a feed which doesn't exist"""
    session: async_scoped_session
    async with get_session() as session:
        user = User(username="test_username")
        session.add(user)
        await session.commit()

        res = await feed_services.unfollow_feed("test_username", "test_feed_link1", session)
        assert not res


@pytest.mark.asyncio
@setup_tests()
async def test_make_posting_which_exists_read() -> None:
    """check if we can make a posting which exists read"""
    session: async_scoped_session
    async with get_session() as session:
        feed = Feed(
            title="Test Feed",
            description="Test Feed Description",
            category="Test Feed Category",
            lang="Dutch",
            link="test_link1",
            copyright_text="Copyright (c) 2010",
        )
        session.add(feed)
        await session.commit()

        posting = Posting(
            title="Test Posting",
            description="Test Posting Description",
            link="posting_link1",
            author="test author",
            published_at=datetime.datetime.now(),
            feed_id=1,
        )
        session.add(posting)

        await session.commit()

        user = User(username="test_username")
        user.followed_feeds.append(feed)
        session.add(user)
        await session.commit()

        res = await feed_services.make_posting_read("test_username", "posting_link1", session)
        assert res

        read_posting_stmt = text("select * from read_postings")
        read_posting = (await session.execute(read_posting_stmt)).one_or_none()
        assert read_posting is not None


@pytest.mark.asyncio
@setup_tests()
async def test_make_posting_which_doesnt_exists_read() -> None:
    """check if we get prevented of reading a posting which does not exist"""
    session: async_scoped_session
    async with get_session() as session:
        user = User(username="test_username")
        session.add(user)
        await session.commit()

        res = await feed_services.make_posting_read("test_username", "posting_link1", session)
        assert not res

        read_posting_stmt = text("select * from read_postings")
        read_posting = (await session.execute(read_posting_stmt)).one_or_none()
        assert read_posting is None


@pytest.mark.asyncio
@setup_tests()
async def test_make_posting_read_for_invalid_user() -> None:
    """check if we get prevented of reading a posting which does not exist"""
    session: async_scoped_session
    async with get_session() as session:
        res = await feed_services.make_posting_read("test_username", "posting_link1", session)
        assert not res

        read_posting_stmt = text("select * from read_postings")
        read_posting = (await session.execute(read_posting_stmt)).one_or_none()
        assert read_posting is None


@pytest.mark.asyncio
@setup_tests()
async def test_make_posting_which_exists_unread() -> None:
    """check if we can make a posting which exists unread"""
    session: async_scoped_session
    async with get_session() as session:
        feed = Feed(
            title="Test Feed",
            description="Test Feed Description",
            category="Test Feed Category",
            lang="Dutch",
            link="test_link1",
            copyright_text="Copyright (c) 2010",
        )
        session.add(feed)
        await session.commit()

        posting = Posting(
            title="Test Posting",
            description="Test Posting Description",
            link="posting_link1",
            author="test author",
            published_at=datetime.datetime.now(),
            feed_id=1,
        )
        session.add(posting)
        await session.commit()

        user = User(username="test_username")
        user.followed_feeds.append(feed)
        session.add(user)
        await session.commit()

        read_posting_stmt = text("insert into read_postings values (1,1)")
        await session.execute(read_posting_stmt)

        res = await feed_services.make_posting_unread("test_username", "posting_link1", session)
        assert res

        read_posting_stmt = text("select * from read_postings")
        read_posting = (await session.execute(read_posting_stmt)).one_or_none()
        assert read_posting is None


@pytest.mark.asyncio
@setup_tests()
async def test_make_posting_which_doesnt_exist_unread() -> None:
    """check if we can make a posting which doesn't exist unread"""
    session: async_scoped_session
    async with get_session() as session:
        user = User(username="test_username")
        session.add(user)
        await session.commit()

        res = await feed_services.make_posting_unread("test_username", "posting_link1", session)
        assert not res


@pytest.mark.asyncio
@setup_tests()
async def test_make_posting_unread_when_user_not_found() -> None:
    """check if we can make a posting unread when user not found"""
    session: async_scoped_session
    async with get_session() as session:
        res = await feed_services.make_posting_unread("test_username", "posting_link1", session)
        assert not res


@pytest.mark.asyncio
@setup_tests()
async def test_get_feed_to_be_updated():
    """check getting feed to be updated correctly"""
    session: async_scoped_session
    async with get_session() as session:
        feed1_active = Feed(
            title="Test title",
            description="Test Feed Description",
            category="Test Feed Category",
            lang="Dutch",
            link="test_link1",
            copyright_text="Copyright (c) 2010",
        )
        feed2_active = Feed(
            title="Test title",
            description="Test Feed Description",
            category="Test Feed Category",
            lang="Dutch",
            link="test_link2",
            copyright_text="Copyright (c) 2010",
        )
        feed3_inactive = Feed(
            title="Test title",
            description="Test Feed Description",
            category="Test Feed Category",
            lang="Dutch",
            link="test_link3",
            copyright_text="Copyright (c) 2010",
            active=False,
        )
        session.add_all([feed1_active, feed2_active, feed3_inactive])
        await session.commit()
        retrieved_feed = await feed_services.get_feeds_to_be_scheduled(session)
        assert len(retrieved_feed) == 2
        assert retrieved_feed[0].link == "test_link1"
        assert retrieved_feed[1].link == "test_link2"


@pytest.mark.asyncio
@setup_tests()
async def test_deactivate_background_refresh():
    """check if feed can be deactivated"""
    session: async_scoped_session
    async with get_session() as session:
        feed_active = Feed(
            title="Test title",
            description="Test Feed Description",
            category="Test Feed Category",
            lang="Dutch",
            link="test_link1",
            copyright_text="Copyright (c) 2010",
            active=True,
        )
        session.add(feed_active)
        await session.commit()
        await feed_services.deactivate_background_refresh(1, session)

        feed_stmt = text("select * from feeds where link = :feed_link")
        feed = (await session.execute(feed_stmt, {"feed_link": "test_link1"})).one()
        assert not feed.active


@pytest.mark.asyncio
@setup_tests()
async def test_deactivate_background_refresh_with_wrong_pk():
    """check deactivate doesn't raise exception if feed does not exist"""
    session: async_scoped_session
    async with get_session() as session:
        await feed_services.deactivate_background_refresh(2, session)


@pytest.mark.asyncio
@setup_tests()
async def test_force_update_when_user_doesnt_exist() -> None:
    """check if we get prevented when use doesn't exist'"""
    session: async_scoped_session
    async with get_session() as session:
        await feed_services.force_update_feed("test_username", "test_feed_link1", session)

        feeds_stmt = text("select count(*) from feeds")
        feeds = (await session.execute(feeds_stmt)).scalar()

        assert feeds == 0, "we shouldn't add more feeds"


@pytest.mark.asyncio
@patch(
    "sendcloud.services.feeds_services.fetch_feed",
    return_value=__create_feed_and_posting_schemas("test_link1", ["posting_link1"]),
)
@setup_tests()
async def test_force_update(feed_fetch_mock: MagicMock) -> None:
    """check if we can force update an inactive feed"""
    session: async_scoped_session
    async with get_session() as session:
        feed_inactive = Feed(
            title="Test title",
            description="Test Feed Description",
            category="Test Feed Category",
            lang="Dutch",
            link="test_link1",
            copyright_text="Copyright (c) 2010",
            active=False,
        )
        session.add(feed_inactive)
        await session.commit()

        user = User(username="test_username")
        session.add(user)
        user.followed_feeds.append(feed_inactive)
        await session.commit()

        await feed_services.force_update_feed("test_username", "test_link1", session)

        feed_fetch_mock.assert_called_with("test_link1")

        feeds_stmt = text("select * from feeds")
        feeds = (await session.execute(feeds_stmt)).all()

        assert len(feeds) == 1
        assert feeds[0].link == "test_link1"
        assert feeds[0].active


#
# @pytest.mark.asyncio
# @setup_tests()
# async def test_filter_following_feed_postings() -> None:
#     """
#     check if we can filter feeds correctly
#
#     test contains following data:
#     1) two users
#     2) inactive feed for both users
#     3) active feed for both users
#     4) feed with read/unread postings
#     5) feeds with different update dates
#     """
#     session: async_scoped_session
#     async with get_session() as session:
#         feed_inactive = Feed(
#             title="Test title",
#             description="Test Feed Description",
#             category="Test Feed Category",
#             lang="Dutch",
#             link="test_link1",
#             copyright_text="Copyright (c) 2010",
#             active=False
#         )
#
#         feed_inactive = Feed(
#             title="Test title",
#             description="Test Feed Description",
#             category="Test Feed Category",
#             lang="Dutch",
#             link="test_link1",
#             copyright_text="Copyright (c) 2010",
#             active=False
#         )
#
#         session.add(feed_inactive)
#         await session.commit()
#
#         user = User(username="test_username")
#         session.add(user)
#         user.followed_feeds.append(feed_inactive)
#         await session.commit()
#
#         await feed_services.filter_following_feed_postings("test_username", "test_link1", session)
#
#
#         feeds_stmt = text("select * from feeds")
#         feeds = (await session.execute(feeds_stmt)).all()
#
#         assert len(feeds) == 1
#         assert feeds[0].link == "test_link1"
#         assert feeds[0].active
