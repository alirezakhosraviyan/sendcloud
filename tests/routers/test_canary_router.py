"""test_canary module"""
import pytest
from fastapi.testclient import TestClient

from sendcloud.apps.api_service import app

fastapi_client = TestClient(app)


@pytest.mark.asyncio
async def test_canary():
    """test canary function to verify the environment has been set up correctly"""
    result = fastapi_client.get("/v1.0/canary/")
    assert result.status_code == 200
