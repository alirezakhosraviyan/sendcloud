"""
Module to fetch a feed from internet
"""
from time import mktime
from datetime import datetime
import logging
from typing import Optional, Tuple, List
import aiohttp
import feedparser

from sendcloud.schemas import FeedItemCreate, PostingItemCreate


logger = logging.getLogger(__name__)


async def fetch_feed(link: str) -> Tuple[Optional[FeedItemCreate], Optional[List[PostingItemCreate]]]:
    """
    Loads a feed for a given link
    :param link: link to be fetched
    :return: Tuples of feed items and their associated postings
    """
    async with aiohttp.ClientSession() as session:
        # NOTE: we used aiohttp due to the feedparser makes blocking http request itself to load xml from link then
        # we would have lost the asynchronous feature
        try:
            async with session.get(link) as response:
                if response.status < 200 or response.status > 299:
                    logger.error("[ERROR] Response received with status code: %s", str(response.status))
                    return None, None
                html = await response.text()
                parsed_xml = feedparser.parse(html)
                if parsed_xml.get("bozo"):
                    logger.error("[ERROR] Feed couldn't be validated for link: %s", link)
                    return None, None

                feed = parsed_xml.get("feed")

                if feed is None:
                    logger.error("[ERROR] Feed couldn't be parsed for link: %s", link)
                    return None, None

                entries = parsed_xml.get("entries", [])
                feed_scheme = FeedItemCreate(
                    link=link,
                    title=feed.get("title", "-"),
                    lang=feed.get("language", "-"),
                    copyright_text=feed.get("copyright", "-"),
                    description=feed.get("summary", "-"),
                    category=feed.get("category", "-"),
                )
                postings_scheme = [
                    PostingItemCreate(
                        link=entry.get("link", "-"),
                        title=entry.get("title", "-"),
                        description=entry.get("summary", "-"),
                        published_at=datetime.fromtimestamp(mktime(entry.get("published_parsed", "-"))),
                        author=entry.get("author", "-"),
                    )
                    for entry in entries
                ]
                return feed_scheme, postings_scheme
        except (
            Exception  # pylint: disable=broad-exception-caught
        ) as error:
            logger.error("[ERROR] Exception in Feed loader , kind: %s, message : %s", type(error), str(error))
            return None, None
