"""Scheduler test Module"""
import pytest
import datetime
from unittest.mock import MagicMock, patch, AsyncMock

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_scoped_session

from sendcloud.utils import get_session
from sendcloud.utils import setup_tests
from sendcloud.models import Feed
from sendcloud.utils.scheduler import Task, Scheduler
from sendcloud.schemas import FeedItemCreate, PostingItemCreate


async def mock_coroutine(error: bool = False) -> None:
    """Mocking async func"""
    if error:
        raise Exception("Finish the infinity loop!")


@pytest.mark.asyncio
@patch("sendcloud.utils.scheduler.sleep", side_effect=mock_coroutine(True))
@patch("sendcloud.utils.scheduler.Task.start", return_value=MagicMock())
@setup_tests()
async def test_run_scheduler(task_start_mock: MagicMock, sleep_mock: MagicMock) -> None:
    """Check if scheduler can be run"""
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
            active=False
        )
        session.add_all([feed1_active, feed2_active, feed3_inactive])
        await session.commit()

        loop = MagicMock()
        loop.create_task = AsyncMock()

        try:
            await Scheduler(300, loop).run()
        except Exception:  # pylint: disable=broad-except
            sleep_mock.assert_called_with(300)
            task_start_mock.assert_called()
            assert loop.create_task.call_count == 2


@pytest.mark.asyncio
@patch("sendcloud.utils.scheduler.sleep", side_effect=mock_coroutine(True))
@patch("sendcloud.utils.scheduler.Task.start", return_value=MagicMock())
@setup_tests()
async def test_run_scheduler_with_no_feed(task_start_mock: MagicMock, sleep_mock: MagicMock) -> None:
    """Check if scheduler takles correctly with empty task list"""
    loop = MagicMock()
    loop.create_task = AsyncMock()

    try:
        await Scheduler(300, loop).run()
    except Exception:  # pylint: disable=broad-except
        sleep_mock.assert_called_with(300)
        task_start_mock.assert_not_called()


@pytest.mark.asyncio
@setup_tests()
async def test_task_on_failure() -> None:
    """Check if task contex manager can deactivate the feed"""
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
        session.add(feed1_active)
        await session.commit()

        task = Task(feed1_active)
        on_failure_handler = getattr(task, "_Task__on_task_failure")
        await on_failure_handler()

        retrieved_feed_stmt = text("select * from feeds")
        retrieved_feed = (await session.execute(retrieved_feed_stmt)).one_or_none()

        assert retrieved_feed is not None
        assert not retrieved_feed[-1]


@pytest.mark.asyncio
@setup_tests()
async def test_task_on_success() -> None:
    """Check if task contex manager can update the feed"""
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
        session.add(feed1_active)
        await session.commit()

        feed = FeedItemCreate(
            link="test_link1",
            title="should be changed to me!",
            lang="feed_lank",
            copyright_text="feed_copyright_test",
            description="test_description",
            category="cat1",
        )
        posting_items = [
            PostingItemCreate(
                link="posting_link1",
                title="posting_title",
                author="posting_author",
                published_at=datetime.datetime.now(),
                description="posting_description",
            )]

        task = Task(feed1_active)
        on_task_success = getattr(task, "_Task__on_task_success")
        await on_task_success((feed, posting_items))

        retrieved_feed_stmt = text("select * from feeds")
        retrieved_feed = (await session.execute(retrieved_feed_stmt)).one_or_none()

        retrieved_posting_stmt = text("select count(*) from postings where feed_id = 1")
        retrieved_posting_count = (await session.execute(retrieved_posting_stmt)).scalar()

        assert retrieved_feed is not None
        assert retrieved_feed[2] == "should be changed to me!"
        assert retrieved_posting_count == 1


@pytest.mark.asyncio
@setup_tests()
async def test_task_on_success_after_retry() -> None:
    """Check if task contex manager can activate the feed"""
    session: async_scoped_session
    async with get_session() as session:
        feed1_inactive = Feed(
            title="Test title",
            description="Test Feed Description",
            category="Test Feed Category",
            lang="Dutch",
            link="test_link1",
            copyright_text="Copyright (c) 2010",
            active=False  # False indicates the task for this feed had some retries
        )
        session.add(feed1_inactive)
        await session.commit()

        feed = FeedItemCreate(
            link="test_link1",
            title="should be changed to me!",
            lang="feed_lank",
            copyright_text="feed_copyright_test",
            description="test_description",
            category="cat1",
        )

        task = Task(feed1_inactive)
        on_task_success = getattr(task, "_Task__on_task_success")
        await on_task_success((feed, []))

        retrieved_feed_stmt = text("select * from feeds")
        retrieved_feed = (await session.execute(retrieved_feed_stmt)).one_or_none()

        assert retrieved_feed is not None
        assert retrieved_feed[-1]
        assert retrieved_feed[2] == "should be changed to me!"


fetch_feed_result = (FeedItemCreate(
    link="test_link1",
    title="should be changed to me!",
    lang="feed_lank",
    copyright_text="feed_copyright_test",
    description="test_description",
    category="cat1",
), [])


@pytest.mark.asyncio
@patch("sendcloud.utils.scheduler.fetch_feed", return_value=AsyncMock(return_value=fetch_feed_result))
@patch("sendcloud.utils.scheduler.sleep", side_effect=mock_coroutine(True))
@setup_tests()
async def test_task_start(sleep_mock: MagicMock, fetch_feed_mock: MagicMock) -> None:
    """Check if task contex manager can be started"""
    feed1_active = Feed(
        title="Test title",
        description="Test Feed Description",
        category="Test Feed Category",
        lang="Dutch",
        link="test_link1",
        copyright_text="Copyright (c) 2010",
        active=True
    )

    task = Task(feed1_active)
    __on_task_success = AsyncMock()
    __on_task_failure = AsyncMock()

    setattr(task, "_Task__on_task_success", __on_task_success)
    setattr(task, "_Task__on_task_failure", __on_task_failure)

    await task.start()

    fetch_feed_mock.assert_called_with("test_link1")
    __on_task_success.assert_called()
    __on_task_failure.assert_not_called()
    sleep_mock.assert_not_called()


@pytest.mark.asyncio
@patch("sendcloud.utils.scheduler.fetch_feed", return_value=(None, None))
@patch("sendcloud.utils.scheduler.sleep")
@setup_tests()
async def test_task_start_can_retry_on_failure_no_success(sleep_mock: MagicMock, fetch_feed_mock: MagicMock) -> None:
    """Check if task contex manager can can retry on failures and even no success"""
    feed1_active = Feed(
        title="Test title",
        description="Test Feed Description",
        category="Test Feed Category",
        lang="Dutch",
        link="test_link1",
        copyright_text="Copyright (c) 2010",
        active=True
    )

    task = Task(feed1_active)
    __on_task_success = AsyncMock()
    __on_task_failure = AsyncMock()

    setattr(task, "_Task__on_task_success", __on_task_success)
    setattr(task, "_Task__on_task_failure", __on_task_failure)

    await task.start()

    fetch_feed_mock.assert_called_with("test_link1")
    assert __on_task_failure.call_count == 1
    assert sleep_mock.call_count == 3
    __on_task_success.assert_not_called()
