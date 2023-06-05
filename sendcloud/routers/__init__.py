"""router module"""
from .canary_router import router
from .users_router import router_v1_0 as user_router_v1_0
from .feeds_router import router_v1_0 as feed_router_v1_0

all_routers = [router, user_router_v1_0, feed_router_v1_0]

__all__ = ["all_routers"]
