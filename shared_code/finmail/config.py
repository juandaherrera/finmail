"""Finmail Configuration Module."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Finmail application settings."""

    # Defaults
    DEFAULT_CATEGORY: str = "Pending Classification"


settings = Settings()
