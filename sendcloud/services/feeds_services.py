"""
Feed database Service, containing functions to fetch data
"""
from typing import List, Optional, Sequence, Tuple
import pydash as _
from sqlalchemy.ext.asyncio import async_scoped_session
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, text, Row, delete, update
from sqlalchemy.orm import selectinload

from sendcloud.models import Feed, User, Posting, user_feed, read_postings
from sendcloud.schemas import FeedItemCreate, PostingItemCreate, OrderByLastUpdate
from sendcloud.utils import fetch_feed
from sendcloud.utils import value_error
from .users_services import get_user_by_username


async def insert_or_update_feed(
    feed: FeedItemCreate, postings: List[PostingItemCreate], session: async_scoped_session
) -> Optional[int]:
    """
    Insert or update a feed for a given user
    :param feed: new feed item
    :param postings: new posting items
    :param session: databse session
    :return: the primary key of the newly added feed
    """
    feed_dict = feed.dict(exclude={"postings"})
    feed_stmt = insert(Feed).values(feed_dict).on_conflict_do_update(constraint="feeds_link_key", set_=feed_dict)
    res = await session.execute(feed_stmt)

    feed_pk: int = res.inserted_primary_key[0]  # type: ignore
    for cur in postings:
        postings_dict = cur.dict()
        postings_dict.update({"feed_id": feed_pk})
        postings_stmt = (
            insert(Posting)
            .values(postings_dict)
            .on_conflict_do_update(constraint="postings_link_key", set_=postings_dict)
        )
        await session.execute(postings_stmt)
    await session.commit()
    return feed_pk


async def get_feed_by_pk(feed_pk: int, session: async_scoped_session) -> Optional[Row[Tuple[Feed]]]:
    """
    Retrieves a feed by id
    :param feed_pk: feed primary key
    :param session: database session
    :return: returns a feed if exists
    """
    stmt = select(Feed).where(Feed.pk == feed_pk).options(selectinload(Feed.postings))
    return (await session.execute(stmt)).one_or_none()


async def follow_new_feed(username: str, link: str, session: async_scoped_session) -> Optional[Feed]:
    """
    Follow a new existing feed or completely new feed which need to be fetched
    :param username: user unique identifier
    :param link: feed unique identifier
    :param session: database session
    :return: returns the followed feed if possible otherwise returns None
    """
    # checking if the user exists and if the feed has been followed already or not!
    stmt = (
        select(User)
        .where(User.username == username)
        .options(selectinload(User.followed_feeds).options(selectinload(Feed.postings)))
    )
    user = (await session.execute(stmt)).one_or_none()
    if user is None:
        return None
    user_pk = user[0].pk
    # return the feed if it was already followed
    if retrieved_feed := _.find(user[0].followed_feeds, lambda item: item.link == link):
        return retrieved_feed
    # in case the feed is new then we try to fetch it (we haven't check if it already exists because for the
    # first time user would like to see the most updated posts)
    loaded_feed, loaded_postings = await fetch_feed(link)
    if loaded_feed and loaded_postings:
        feed_pk = await insert_or_update_feed(loaded_feed, loaded_postings, session)
        if feed_pk is not None:
            values = {"user_pk": user_pk, "feed_pk": feed_pk}
            stmt_rel = insert(user_feed).values(values).on_conflict_do_nothing(constraint="user_feed_pkey")
            await session.execute(stmt_rel)
            await session.commit()
            if feed := await get_feed_by_pk(feed_pk, session):
                return feed[0]
    return None


async def unfollow_feed(username: str, feed_link: str, session: async_scoped_session) -> bool:
    """
    Unfollow a user from a feed
    :param username: user unique identifier
    :param feed_link: feed unique identifier
    :param session: database session
    :return: True if successfully unfollowed
    """
    # First we fetch the user
    user = await get_user_by_username(username, session)
    if user is None:
        return False

    # Second fetch the feed
    stmt = select(Feed).options(selectinload(Feed.postings)).where(Feed.link == feed_link)
    feed = (await session.execute(stmt)).one_or_none()
    if feed is None:
        return False

    # Third if all checks passed then we can unfollow the feed!
    feed = feed[0]
    unfollow_feed_stmt = text("delete from user_feed where user_pk=:user_pk and feed_pk=:feed_pk")
    await session.execute(unfollow_feed_stmt, {"user_pk": user.pk, "feed_pk": feed.pk})  # type: ignore

    # Forth we need to clean the read history
    delete_stmt = delete(read_postings).where(
        User.pk == user.pk, Posting.pk.in_(_.map_(feed.postings, lambda index: index.pk))  # type: ignore
    )
    await session.execute(delete_stmt)
    await session.commit()
    return True


async def make_posting_read(username: str, posting_link: str, session: async_scoped_session) -> bool:
    """
    Adds a posting to user seen collection postings
    :param username: the user unique identifier
    :param posting_link: the posting unique identifier
    :param session: database async session
    :return: True if user is eligible to read the posting
    """
    # First we fetch the user
    user = await get_user_by_username(username, session)
    if user is None:
        return False

    # Second we check posting existence
    stmt = select(Posting).where(Posting.link == posting_link)
    posting = (await session.execute(stmt)).one_or_none()
    if posting is None:
        return False

    # Third we check the related feed is followed by the user
    user_feed_stmt = text("select * from user_feed where feed_pk = :feed_pk and user_pk = :user_pk")
    user_is_allowed_to_read = (
        await session.execute(user_feed_stmt, {"feed_pk": posting[0].feed_id, "user_pk": user.pk})
    ).one_or_none()
    if user_is_allowed_to_read is None:
        return False

    # Forth if all check passed then we can make the posting read!
    posting_read_stmt = (
        insert(read_postings)
        .values({"user_pk": user.pk, "posting_pk": posting[0].pk})
        .on_conflict_do_nothing(constraint="read_postings_pkey")
    )
    await session.execute(posting_read_stmt)
    await session.commit()
    return True


async def make_posting_unread(username: str, posting_link: str, session: async_scoped_session) -> bool:
    """
    Removes a posting from users seen collection
    :param username: the user unique identifier
    :param posting_link: the posting unique identifier
    :param session: database async session
    :return: True if user is eligible to unread the posting
    """
    # First we fetch the user
    user = await get_user_by_username(username, session)
    if user is None:
        return False

    # Second fetch the posting id and also check if it exists
    stmt = select(Posting).where(Posting.link == posting_link)
    posting = (await session.execute(stmt)).one_or_none()
    if posting is None:
        return False

    # Third if all checks passed then we can make the posting unread!
    posting_unread_stmt = delete(read_postings).where(Posting.link == posting_link)
    await session.execute(posting_unread_stmt)
    await session.commit()
    return True


def __get_feed_ids(feed_link: Optional[str], feed_collection: List[Feed]) -> List[int]:
    filtered_feeds = (
        _.filter_(feed_collection, lambda index: index.link == feed_link and index.active) if feed_link is not None else _.filter_(feed_collection, lambda index: index.active)
    )
    return _.map_(filtered_feeds, lambda index: int(index.pk))


# pylint: disable=too-many-arguments
async def filter_following_feed_postings(
    username: str,
    feed_link: Optional[str],
    is_read: Optional[bool],
    order_by: OrderByLastUpdate,
    session: async_scoped_session,
    offset: int = 0,
    limit: int = 10,
) -> Sequence[Row]:
    """
    Filters the user's postings based on the last update, read status and feed
    :param username: user unique identifier
    :param feed_link: user unique identifier
    :param is_read: posting has been read by the user or not
    :param order_by: order postings based on last time has been updated
    :param session: database session
    :param offset:
    :param limit:
    :return:
    """
    user_detailed_stmt = select(User).options(selectinload(User.followed_feeds)).where(User.username == username)
    user_detailed = await session.scalar(user_detailed_stmt)
    if user_detailed is None:
        value_error("user not found")
        return []

    order_stm = (
        Posting.updated_at.desc() if order_by == OrderByLastUpdate.LAST_UPDATE_DESCENDING else Posting.updated_at.asc()
    )

    stmt = select(Posting).where(Posting.feed_id.in_(__get_feed_ids(feed_link, user_detailed.followed_feeds)))

    if is_read is not None:
        read_posting_ids_stmt = text("select posting_pk from read_postings where user_pk = :user_pk")
        read_posting_ids = [cur[0] for cur in (await session.execute(read_posting_ids_stmt, {"user_pk": user_detailed.pk})).all()]
        stmt = stmt.where(Posting.pk.in_(read_posting_ids) if is_read else Posting.pk.notin_(read_posting_ids))

    stmt = stmt.order_by(order_stm).offset(offset).limit(limit)
    postings = (await session.scalars(stmt)).all()
    return postings


async def get_feeds_to_be_scheduled(session: async_scoped_session) -> List[Feed]:
    """
    Returns a list of feed links to be scheduled
    :param session: the database session
    :return: List of feed's link
    """
    feeds_stmt = select(Feed.pk, Feed.link, Feed.active).where(Feed.active == True)
    return (await session.execute(feeds_stmt)).all()  # type: ignore


async def deactivate_background_refresh(feed_pk: int, session: async_scoped_session) -> None:
    update_stmt = (
        update(Feed)
        .where(Feed.pk == feed_pk)
        .values({"active": False})
        .execution_options(synchronize_session="fetch")
    )
    await session.execute(update_stmt)
    await session.commit()


async def force_update_feed(username: str, feed_link: str, session: async_scoped_session) -> bool:
    # checking if the user exists
    user = await get_user_by_username(username, session)
    if user is None:
        return False

    loaded_feed, loaded_postings = await fetch_feed(feed_link)
    if loaded_feed and loaded_postings:
        feed_pk = await insert_or_update_feed(loaded_feed, loaded_postings, session)
        if feed_pk is not None:
            values = {"user_pk": user.pk, "feed_pk": feed_pk}
            stmt_rel = insert(user_feed).values(values).on_conflict_do_nothing(constraint="user_feed_pkey")
            await session.execute(stmt_rel)
            await session.commit()
            return True
    return False
