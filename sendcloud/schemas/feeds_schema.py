"""
Contains all the schema related to feed and postings
"""
from enum import Enum
from typing import List
from datetime import datetime
from pydantic import BaseModel  # pylint: disable=no-name-in-module


# pylint: disable=too-few-public-methods
class PostingItem(BaseModel):
    """
    Schema for retrieving posting with default for docs
    """

    link: str = "https://www.nu.nl/buitenland/6266360/dodental-treinramp-india-nadert-de-300-zeker-900-gewonden.html"
    title: str = "Dodental treinramp India nadert de 300, zeker 900 gewonden"
    author: str = "onze nieuwsredactie"
    published_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    description: str = (
        "Het aantal dodelijke slachtoffers van de treinramp in het oosten van India vrijdag is opgelopen tot zeker 288."
    )

    class Config:
        """schema config"""

        orm_mode = True


# pylint: disable=too-few-public-methods
class PostingItemCreate(BaseModel):
    """
    Schema for creating a posting item
    """

    link: str
    title: str
    author: str
    published_at: datetime
    description: str

    class Config:
        """schema config"""

        orm_mode = True


# pylint: disable=too-few-public-methods
class FeedItem(BaseModel):
    """
    Schema for listing feed items with default for docs
    """

    link: str = "https://feeds.rijksoverheid.nl/woo-besluiten.rss"
    title: str = "Rijksoverheid.nl - Woo-besluiten"
    lang: str = "nl-NL"
    copyright_text = "Iedere vorm van hergebruik van de inhoud van deze feed is toegestaan"
    description: str = "Woo-besluiten op Rijksoverheid.nl"
    category: str = "Woo-besluiten"
    created_at: str = "Tue, 30 May 2023 18:51:06 GMT"

    postings: List[PostingItem]

    class Config:
        """schema config"""

        orm_mode = True


# pylint: disable=too-few-public-methods
class FeedItemCreate(BaseModel):
    """
    Schema for creating Feed
    """

    link: str
    title: str
    lang: str
    copyright_text: str
    description: str
    category: str
    active: bool = True

    class Config:
        """schema config"""

        orm_mode = True


# pylint: disable=too-few-public-methods
class FollowingFeedInput(BaseModel):
    """
    Schema for FollowingFeed input
    """

    username: str
    link: str


# pylint: disable=too-few-public-methods
class FollowingFeedsCreateResult(BaseModel):
    """
    Schema for return the result of creating a new feed
    """

    message: str = "Feed followed successfully"
    feed: FeedItemCreate


# pylint: disable=too-few-public-methods
class FollowingFeedPostings(BaseModel):
    """
    Schema for listing the postings of a feed
    """

    postings: List[PostingItem]


# pylint: disable=too-few-public-methods
class OrderByLastUpdate(Enum):
    """
    OrderBy enum for list api feed parameters
    """

    LAST_UPDATE_ASCENDING = "last_update"
    LAST_UPDATE_DESCENDING = "-last_update"
