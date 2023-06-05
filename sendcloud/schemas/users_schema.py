"""
Contains all the schema related to user
"""
from typing import List
from pydantic import BaseModel  # pylint: disable=no-name-in-module


# pylint: disable=too-few-public-methods
class FollowingFeed(BaseModel):
    """
    Schema for listing the following feeds
    """

    title: str
    link: str

    class Config:
        """schema config"""

        orm_mode = True


# pylint: disable=too-few-public-methods
class UserItem(BaseModel):
    """
    Schem for listing the user item information
    """

    username: str = "alireza"
    followed_feeds: List[FollowingFeed]

    class Config:
        """schema config"""

        orm_mode = True


# pylint: disable=too-few-public-methods
class UserInput(BaseModel):
    """
    Schema for receiving username
    """

    username: str

    class Config:
        """schema config"""

        orm_mode = True


# pylint: disable=too-few-public-methods
class UserCreateOutput(BaseModel):
    """
    Schema for result of user creation
    """

    message: str = "User created successfully"
