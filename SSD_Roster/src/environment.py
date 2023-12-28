__all__ = ("SETTINGS",)


from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="ignore",
        env_file=("../.env", "../.env.prod"),
        env_file_encoding="utf-8",
    )

    TITLE: str
    HOST: str
    PORT: int
    ENVIRONMENT: Literal["production", "development"]


SETTINGS = Settings()
