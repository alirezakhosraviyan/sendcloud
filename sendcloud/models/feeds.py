"""FeedModel Module"""
from typing import List
from sqlalchemy import Column, Integer, VARCHAR, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.orm import validates
from sqlalchemy import Table

from sendcloud.utils import Base


# pylint: disable=too-few-public-methods
class Feed(Base):
    """Feed model class to store data"""

    __tablename__ = "feeds"

    pk = Column(Integer, primary_key=True, index=True, autoincrement=True)
    link = Column(VARCHAR(512), nullable=False, unique=True)
    title = Column(VARCHAR(255), nullable=False)
    lang = Column(VARCHAR(20), nullable=False)
    copyright_text = Column(VARCHAR(1024), nullable=False)
    description = Column(VARCHAR(1024), nullable=False)
    category = Column(VARCHAR(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())  # pylint: disable=not-callable

    entries: Mapped[List["Entry"]] = relationship("Entry", back_populates="feed", cascade="all, delete-orphan")

    @validates("link")
    def validate_link(self, _, link) -> str:
        """check if link has enough characters"""
        if len(link) <= 3:
            raise ValueError("link too short")
        return link


read_entries = Table(
    "read_entries",
    Base.metadata,
    Column("entry_pk", Integer, ForeignKey("entries.pk"), primary_key=True),
    Column("user_pk", Integer, ForeignKey("users.pk"), primary_key=True),
)


class Entry(Base):
    """Entry model class to store data"""

    __tablename__ = "entries"

    pk = Column(Integer, primary_key=True, index=True, autoincrement=True)
    link = Column(VARCHAR(512), nullable=False, unique=True)
    title = Column(VARCHAR(255), nullable=False)
    description = Column(VARCHAR(1024), nullable=False)
    feed_id = Column(Integer, ForeignKey("feeds.pk"), nullable=False)
    read_by: Mapped[List["User"]] = relationship("User", secondary=read_entries)  # type: ignore

    feed: Mapped[Feed] = relationship("Feed", back_populates="entries")
