"""
Contains the user related routes
"""
from typing import List, Sequence
from fastapi import Depends, APIRouter
from sqlalchemy import Row

from sqlalchemy.ext.asyncio import async_scoped_session

from sendcloud.schemas import UserItem, UserInput
from sendcloud.services import users_services as users_services
from sendcloud.utils import get_session_injector

# routers
router_v1_0 = APIRouter(prefix="/v1.0/users")


@router_v1_0.get("/", status_code=200, response_model=List[UserItem])
async def list_users(
    offset: int = 0, limit: int = 100, session: async_scoped_session = Depends(get_session_injector)
) -> Sequence[Row]:
    """
    Retrieves the list of all user's information
    :param offset: pagination offset
    :param limit: pagination limit
    :param session: database session which is being injected by fastapi
    :return:
    """
    return await users_services.get_users(session, offset=offset, limit=limit)


@router_v1_0.post("/", status_code=201)
async def create_user(user: UserInput, session: async_scoped_session = Depends(get_session_injector)) -> None:
    """
    Create a new user
    :param user: contains user information
    :param session: database session which is being injected by fastapi
    :return:
    """
    await users_services.create_user(user.username, session)
