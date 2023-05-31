"""
Simple Endpoint to test fastapi works fine
"""
from fastapi import APIRouter

# routers
router = APIRouter(prefix="/v1.0/canary")


@router.get("/")
async def canary():
    """test canary endpoint"""
