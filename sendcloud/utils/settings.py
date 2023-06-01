"""Setting module"""
from pydantic import BaseSettings


# pylint: disable=too-few-public-methods
class Settings(BaseSettings):
    """Settings class which contains all environment variables"""

    app_name: str = "SendCloud"
    database_url: str = "sqlite:///./db.sqlite"
    environment: str = "dev"


settings = Settings()

if settings.environment == "test":
    settings.database_url = "sqlite+aiosqlite:///.unittest.sqlite"
