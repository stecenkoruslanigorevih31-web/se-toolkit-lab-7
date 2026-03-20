"""
Configuration loading from environment variables.

Uses pydantic-settings to load and validate environment variables
from .env.bot.secret file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Bot configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env.bot.secret",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str = ""
    lms_api_url: str = "http://localhost:42002"
    lms_api_key: str = ""
    llm_api_key: str = ""
    llm_api_base_url: str = ""
    llm_api_model: str = ""


def load_config() -> BotSettings:
    """Load bot configuration from environment."""
    return BotSettings()
