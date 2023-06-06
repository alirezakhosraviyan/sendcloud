"""
Contains the feed related routes
"""
from typing import Optional, Sequence, Dict
from fastapi import Depends, APIRouter, Query
from sqlalchemy import Row
from sqlalchemy.ext.asyncio import async_scoped_session

from sendcloud.utils import get_session_injector
from sendcloud.utils import value_error
from sendcloud.services import feeds_services as feed_services
from sendcloud.schemas import FollowingFeedsCreateResult, FollowingFeedPostings, FollowingFeedInput, OrderByLastUpdate
from sendcloud.models import Feed

router_v1_0 = APIRouter(prefix="/v1.0/feeds")


@router_v1_0.patch("/postings/read", status_code=200)
async def mark_posting_read(
    body: FollowingFeedInput, session: async_scoped_session = Depends(get_session_injector)
) -> None:
    """
    Mark a feed as read for a specific user
    :param body: the feed and the username
    :param session: the database session which is being injected by fastapi
    :return:
    """
    if not await feed_services.make_posting_read(body.username, body.link, session):
        value_error("not allowed to read this posting")


@router_v1_0.patch("/postings/unread", status_code=200)
async def mark_posting_unread(
    body: FollowingFeedInput, session: async_scoped_session = Depends(get_session_injector)
) -> None:
    """
    Mark a post as unread for a specific user
    :param body: the feed and the username
    :param session: the database session which is being injected by fastapi
    :return: None
    """
    if not await feed_services.make_posting_unread(body.username, body.link, session):
        value_error("not allowed to unread this posting")


@router_v1_0.post("/follow", status_code=200, response_model=FollowingFeedsCreateResult)
async def follow_new_feed(
    new_feed: FollowingFeedInput, session: async_scoped_session = Depends(get_session_injector)
) -> Optional[Dict[str, Optional[Feed]]]:
    """
    Follow a new feed for a user with the given feed link
    :param new_feed: contains the feed link and the username
    :param session: database session which is being injected by fastapi
    :return: the newly followed feed or None
    """
    if feed := await feed_services.follow_new_feed(new_feed.username, new_feed.link, session):
        return {"feed": feed}
    return value_error("feed or user not found")


@router_v1_0.delete("/unfollow", status_code=200)
async def unfollow_feed(
    feed_to_be_deleted: FollowingFeedInput, session: async_scoped_session = Depends(get_session_injector)
) -> None:
    """
    Unfollow a feed for a user with the given feed link
    :param feed_to_be_deleted: contains a feed link and a username
    :param session: database session which is being injected by fastapi
    :return: None
    """
    if not await feed_services.unfollow_feed(feed_to_be_deleted.username, feed_to_be_deleted.link, session):
        value_error("feed or user not found")


@router_v1_0.get("/following/postings", status_code=200, response_model=FollowingFeedPostings)
async def get_all_following_feed_postings(
    username: str,
    feed_link: Optional[str] = None,
    is_read: Optional[bool] = Query(default=None),
    order_by: OrderByLastUpdate = OrderByLastUpdate.LAST_UPDATE_DESCENDING,
    offset: int = 0,
    limit: int = 10,
    session: async_scoped_session = Depends(get_session_injector),
) -> Dict[str, Sequence[Row]]:
    # pylint: disable=too-many-arguments
    """
    Retrieve the all postings for the feeds which has been followed by a user
    :param username:
    :param feed_link: the unique feed identifier
    :param is_read: indicates the retrieved posting should be read or unread
    :param order_by: indicates the order parameter
    :param offset: pagination offset
    :param limit: pagination limit
    :param session: database session which is being injected by fastapi
    :return: None
    """
    postings = await feed_services.filter_following_feed_postings(
        username, feed_link, is_read, order_by, session, offset, limit
    )
    return {"postings": postings}


@router_v1_0.post("/feed/force-update", status_code=200)
async def force_update_feed(
    feed_to_be_updated: FollowingFeedInput, session: async_scoped_session = Depends(get_session_injector)
) -> None:
    """
    Each feed gets deactivated after three times failure in refreshing but user can force update a feed, and it will be
    activated again if it was successful
    :param feed_to_be_updated: the feed link which should be updated
    :param session:
    :return:
    """
    if not await feed_services.force_update_feed(feed_to_be_updated.username, feed_to_be_updated.link, session):
        value_error("Unfortunately update was not successful")
