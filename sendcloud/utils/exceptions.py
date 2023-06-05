"""Custom Exception Module"""
from fastapi import HTTPException


def value_error(message: str):
    """
    raise http exception for error message
    :param message: the error message
    :return:
    """
    raise HTTPException(detail=message, status_code=400)
