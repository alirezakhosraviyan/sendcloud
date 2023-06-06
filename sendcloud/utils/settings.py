"""Setting module"""
from pydantic import BaseSettings


# pylint: disable=too-few-public-methods
class Settings(BaseSettings):
    """
    Settings class which contains all environment variables
    """

    app_name: str = "SendCloud"
    database_url: str = "sqlite+aiosqlite:///database.db"


settings = Settings()
