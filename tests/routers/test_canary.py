"""test_canary module"""

from sendcloud.apps.main import app
from fastapi.testclient import TestClient
import pytest


fastapi_client = TestClient(app)


@pytest.mark.asyncio
async def test_canary():
    result = fastapi_client.get('/v1.0/canary/')
    assert result.status_code == 200
