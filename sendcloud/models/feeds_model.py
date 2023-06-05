"""FeedModel Module"""
from typing import List
from sqlalchemy import Column, Integer, VARCHAR, ForeignKey, TIMESTAMP, func, DateTime, Boolean
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.orm import validates
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import Table

from sendcloud.utils import Base


# pylint: disable=too-few-public-methods
class Feed(AsyncAttrs, Base):
    """
    Feed model class to store data
    """

    __tablename__ = "feeds"

    pk = Column(Integer, primary_key=True, index=True, autoincrement=True)
    link = Column(VARCHAR(512), nullable=False, unique=True)
    title = Column(VARCHAR(255), nullable=False)
    lang = Column(VARCHAR(30), nullable=False)
    copyright_text = Column(VARCHAR(1024), nullable=False)
    description = Column(VARCHAR(1024), nullable=False)
    category = Column(VARCHAR(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())  # pylint: disable=not-callable
    active = Column(Boolean, default=True)

    postings: Mapped[List["Posting"]] = relationship("Posting", back_populates="feed", cascade="all, delete-orphan")

    @validates("link")
    def validate_link(self, _, link) -> str:
        """
        Check if link has enough characters
        :param _: ignoring parameter
        :param link: the link to check
        :return: clean field or exception
        """
        if len(link) <= 3:
            raise ValueError("link too short")
        return link


read_postings = Table(
    "read_postings",
    Base.metadata,
    Column("posting_pk", Integer, ForeignKey("postings.pk"), primary_key=True),
    Column("user_pk", Integer, ForeignKey("users.pk"), primary_key=True),
)


class Posting(Base):
    """
    Posting model class to store data
    """

    __tablename__ = "postings"

    pk = Column(Integer, primary_key=True, index=True, autoincrement=True)
    link = Column(VARCHAR(512), nullable=False, unique=True)
    title = Column(VARCHAR(255), nullable=False)
    description = Column(VARCHAR(1024), nullable=False)
    author = Column(VARCHAR(1024), nullable=False)
    published_at = Column(DateTime, nullable=False)
    # pylint: disable=not-callable
    updated_at = Column(DateTime, server_onupdate=func.now(), server_default=func.now())  # type: ignore
    feed_id = Column(Integer, ForeignKey("feeds.pk"), nullable=False)
    read_by: Mapped[List["User"]] = relationship("User", secondary=read_postings)  # type: ignore

    feed: Mapped[Feed] = relationship("Feed", back_populates="postings")
