"""
A test decorator for async pytest tests
"""
from typing import Callable
from functools import wraps
from sqlalchemy.orm import declarative_base

from .db_manager import update_async_database_tables, EDatabaseManipulationType

Base = declarative_base()


def setup_tests(setup_func: Callable = lambda: None):
    """Decorator to set up and teardown unittests"""

    def decorate(callback):
        """Inner decorator function"""

        @wraps(callback)
        async def wrapper(*args, **kwargs):
            await update_async_database_tables(EDatabaseManipulationType.CREATE)
            setup_func()
            result = await callback(*args, **kwargs)
            await update_async_database_tables(EDatabaseManipulationType.DROP)
            return result

        return wrapper

    return decorate
