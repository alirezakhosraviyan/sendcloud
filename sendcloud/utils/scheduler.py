"""
Scheduler Module:
    Task:
        A task is created to update a feed. In case the feed is available, the update will be successful and the feed
        is allowed to be updated, otherwise the feed will be deactivated with the first error to prevent it from being
        scheduled again. 3 more attempts will be made to update the feed, if the task is successful, it will be
        activated again, otherwise, the feed will remain inactive.
    Scheduler:
        The scheduler loads all active feeds once every X-time and creates a task for each of them. Since the tasks are
        executed in async, then the IO will not be blocked. Since the tasks are mostly IO-band factor, it is better to
        use async instead of multiprocessing as long as the 'xml parsing part' is not the case of CPU-bound factor.
"""
import asyncio
from asyncio import sleep
from typing import List, Tuple, Optional
import logging
from sqlalchemy.ext.asyncio import async_scoped_session

from sendcloud.utils import fetch_feed, get_session
from sendcloud.schemas import FeedItemCreate, PostingItemCreate
from sendcloud.services import feeds_services as feed_services
from sendcloud.models import Feed

_LOGGER = logging.getLogger(__name__)


#  pylint: disable=too-few-public-methods
class Task:
    """
    A task is created to update a feed
    """

    def __init__(self, feed: Feed):
        self.__feed = feed

    async def __on_task_success(self, loaded_feed: Tuple[FeedItemCreate, List[PostingItemCreate]]) -> None:
        """
        In case the feed is available and parsed successfully, then it will be inserted/updated in the database
        :param loaded_feed: new update for the given feed
        :return: None
        """
        session: async_scoped_session
        async with get_session() as session:
            await feed_services.insert_or_update_feed(loaded_feed[0], loaded_feed[1], session)
            _LOGGER.debug(
                "[DEBUG] Feed with link : %s successfully updated with %s postings",
                self.__feed.link,
                len(loaded_feed[1]),
            )

    async def __on_task_failure(self) -> None:
        """
        Deactivate feed to prevent of being scheduled
        :return: None
        """
        session: async_scoped_session
        async with get_session() as session:
            await feed_services.deactivate_background_refresh(int(self.__feed.pk), session)

    async def start(self) -> None:
        """
        Create a task to update the given feed, attempts 3 times in 2,5 and 8 minutes
        :return: None
        """
        for retry in range(2, 9, 3):
            loaded_feed = await fetch_feed(str(self.__feed.link))
            if loaded_feed != (None, None):
                await self.__on_task_success(loaded_feed)  # type: ignore
                break
            if retry == 2:
                # in case the feed is not available we immediately make it deactivate to prevent from being scheduled
                # while it still needs to be retried
                await self.__on_task_failure()
            _LOGGER.debug("[DEBUG] Task failed for link : %s , sleeping for %s", self.__feed.link, retry * 60)
            await sleep(retry * 60)


#  pylint: disable=too-few-public-methods
class Scheduler:
    """
    Crates task for each feed once every X-time
    """

    def __init__(self, time_interval: int, loop: Optional[asyncio.AbstractEventLoop]):
        """
        Constructor
        :param time_interval: sleep time for scheduler between each scheduling iteration in second
        :param loop: async loop
        """
        self.__time_interval = time_interval
        self.__loop = loop or asyncio.get_running_loop()

    @staticmethod
    async def __load_feeds_to_be_scheduled() -> List[Feed]:
        """
        Loads all active feeds
        :return: list of feeds
        """
        session: async_scoped_session
        async with get_session() as session:
            feeds = await feed_services.get_feeds_to_be_scheduled(session)
            _LOGGER.debug("[DEBUG] %s feeds are ready to be scheduled", len(feeds))
            return feeds

    async def run(self) -> None:
        """
        Entry point of the main scheduler which reads database every X-time and if there is any active feed then
        schedules them for update via creating a task
        :return: None
        """
        _LOGGER.info("[INFO] Scheduler is running ... ")
        while True:
            feeds_to_be_scheduled = await self.__load_feeds_to_be_scheduled()
            for feed in feeds_to_be_scheduled:
                task = Task(feed)
                self.__loop.create_task(task.start())
            _LOGGER.debug("[DEBUG] sleeping for %s", self.__time_interval)
            await sleep(self.__time_interval)
