__all__ = ("settings",)


# standard library
from pathlib import Path

# third party
from pydantic_settings import BaseSettings, SettingsConfigDict

# typing
from pydantic import BaseModel, SecretStr
from pydantic.networks import AnyUrl, EmailStr, UrlConstraints
from typing import Annotated, Literal


class Database(BaseModel):
    URL: Annotated[AnyUrl, UrlConstraints(allowed_schemes=["sqlite"])]
    CREATE_OWNER: bool
    OWNER_USERNAME: str
    OWNER_PASSWORD: SecretStr
    OWNER_EMAIL: EmailStr


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="ignore",
        env_file=((__env := Path(__file__).parents[2].joinpath(".env")), __env.with_suffix(".prod")),
        # .env-files are located in the same directory as the python package, not inside it
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    TITLE: str
    HOST: str
    PORT: int
    ENVIRONMENT: Literal["production", "development"]
    DATABASE: Database

    OVERRIDE_422_WITH_400: bool = True


settings = Settings()
