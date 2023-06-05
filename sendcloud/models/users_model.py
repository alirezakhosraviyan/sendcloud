"""UserModel Module"""
from typing import List
from sqlalchemy import Column, Integer, VARCHAR, ForeignKey
from sqlalchemy.orm import validates, relationship, Mapped
from sqlalchemy import Table
from sqlalchemy.ext.asyncio import AsyncAttrs
from sendcloud.utils import Base
from sendcloud.models.feeds_model import Feed


user_feed = Table(
    "user_feed",
    Base.metadata,
    Column("feed_pk", Integer, ForeignKey("feeds.pk"), primary_key=True),
    Column("user_pk", Integer, ForeignKey("users.pk"), primary_key=True),
)


# pylint: disable=too-few-public-methods
class User(AsyncAttrs, Base):
    """
    User model clss to store data
    """

    __tablename__ = "users"

    pk = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(VARCHAR(255), nullable=False, unique=True)

    followed_feeds: Mapped[List[Feed]] = relationship("Feed", secondary=user_feed)

    @validates("username")
    def validate_username(self, _, username) -> str:
        """
        check if username has enough characters
        :param _: ignoring the parameter
        :param username: the username to check
        :return: clean username or exception
        """
        if len(username) <= 2:
            raise ValueError("username too short")
        return username
