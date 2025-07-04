"""
Application settings module.

This module defines environment-based configuration using Pydantic's BaseSettings.
It also provides a preconfigured Hypercorn server config via a property.
"""

from hypercorn import Config
from pydantic_settings import BaseSettings

from app.common.helpers import abs_path


class Settings(BaseSettings):
    """
    Application configuration class.

    Inherits:
        BaseSettings: Automatically loads values from environment variables or `.env` file.

    Attributes:
        PROJECT (str): Project name identifier.
        FULL_LOGS (bool): Enables full logging output if True.
        REDIS_HOST (str | None): Redis server hostname.
        REDIS_PORT (int | None): Redis server port.

    Class Config:
        Specifies that environment variables are loaded from `.env`.

    Properties:
        hypercorn_config: Returns a preconfigured Hypercorn Config object.
    """

    PROJECT: str = "marathonbet"

    FULL_LOGS: bool = True

    REDIS_HOST: str | None = "localhost"
    REDIS_PORT: int | None = 6379

    class Config:
        """
        Pydantic configuration for loading environment variables from `.env` file.
        """
        env_file = abs_path(".env")
        env_file_encoding = 'utf-8'

    @property
    def hypercorn_config(self):
        """
        Returns a Hypercorn Config object pre-bound to 0.0.0.0:8080.

        Useful for running ASGI servers in containerized environments.

        Returns:
            Config: A configured Hypercorn instance.
        """
        hypercorn_config = Config()
        hypercorn_config.bind = ['0.0.0.0:8080']

        return hypercorn_config


# Singleton instance of the settings object
settings = Settings()
