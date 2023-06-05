"""tests for exception module"""
from fastapi.exceptions import HTTPException

from sendcloud.utils import value_error


def test_value_error():
    """checks if value_error raised correctly"""
    try:
        value_error("this is a test")
    except HTTPException as error:
        assert str(error.detail) == "this is a test"
