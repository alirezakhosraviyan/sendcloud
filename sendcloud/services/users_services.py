"""
User database Service, containing functions to fetch data
"""
from typing import Sequence, Optional
from sqlalchemy.ext.asyncio import async_scoped_session
from sqlalchemy.orm import selectinload
from sqlalchemy import Row
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from sendcloud.models import User
from sendcloud.utils import value_error


async def get_users(session: async_scoped_session, offset: int = 0, limit: int = 100) -> Sequence[Row]:
    """
    Function to retrieve users with limited data for following feeds
    :param session: database session
    :param offset: pagination offset
    :param limit: pagination limit
    :return: all the users
    """
    stmt = select(User).limit(limit).offset(offset).options(selectinload(User.followed_feeds))
    return (await session.scalars(stmt)).all()


async def create_user(username: str, session: async_scoped_session) -> None:
    """
    Creates a new user
    :param username: the username
    :param session: database session
    :return:
    """
    try:
        user = User(username=username)
        session.add(user)
        await session.commit()
    except IntegrityError:
        value_error("User Already Exists")


async def get_user_by_username(username: str, session: async_scoped_session) -> Optional[User]:
    """
    Retrieve user by username
    :param username: user unique identifier
    :param session: database session
    :return:
    """
    stmt = select(User).where(User.username == username)
    if res := (await session.execute(stmt)).one_or_none():
        return res[0]
    return None
