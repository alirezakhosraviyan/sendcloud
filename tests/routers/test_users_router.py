"""test users routers"""
from typing import List
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

from sendcloud.apps.api_service import app
from sendcloud.models import User, Feed
from sendcloud.utils import setup_tests

fastapi_client = TestClient(app)


def __get_users_with_feeds() -> List[User]:
    """creates sample user data"""
    users = [User(username="testuser1"), User(username="testuser2")]

    feed_inactive = Feed(
        title="Test title",
        description="Test Feed Description",
        category="Test Feed Category",
        lang="Dutch",
        link="test_link1",
        copyright_text="Copyright (c) 2010",
        active=False,
    )

    feed2_active = Feed(
        title="Test title2",
        description="Test Feed Description",
        category="Test Feed Category",
        lang="Dutch",
        link="test_link2",
        copyright_text="Copyright (c) 2010",
        active=True,
    )

    feed3_active = Feed(
        title="Test title3",
        description="Test Feed Description",
        category="Test Feed Category",
        lang="Dutch",
        link="test_link3",
        copyright_text="Copyright (c) 2010",
        active=False,
    )

    users[0].followed_feeds.append(feed_inactive)
    users[0].followed_feeds.append(feed2_active)
    users[1].followed_feeds.append(feed3_active)

    return users


@pytest.mark.asyncio
@patch("sendcloud.services.users_services.get_users", return_value=__get_users_with_feeds())
@setup_tests()
async def test_get_all_users(get_users_mocker: MagicMock):
    """test can retrieve all users with feeds"""
    result = fastapi_client.get("/v1.0/users/")

    get_users_mocker.assert_called()
    assert result.status_code == 200

    assert len(result.json()) == 2
    assert result.json()[0]["username"] == "testuser1"
    assert len(result.json()[0]["followed_feeds"]) == 2


@pytest.mark.asyncio
@patch("sendcloud.services.users_services.create_user", return_value=None)
@setup_tests()
async def test_create_user(get_users_mocker: MagicMock):
    """test can create a user"""
    result = fastapi_client.post("/v1.0/users/", json={"username": "testuser1"})

    assert result.status_code == 201
    get_users_mocker.assert_called()
