from pathlib import Path

from pydantic import ConfigDict
from pydantic_settings import BaseSettings

env_file = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    """Provides all project settings and takes some settings,
    such as "BOT_API_TOKEN", from .env.
    """

    bot_api_token: str

    model_config = ConfigDict(
        extra="ignore",
        env_file=env_file if env_file.exists() else None,
        env_file_encoding="utf-8",
    )


settings = Settings()
