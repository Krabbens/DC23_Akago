from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_username: str = Field(alias="MONGO_INITDB_ROOT_USERNAME")
    db_password: str = Field(alias="MONGO_INITDB_ROOT_PASSWORD")
    email: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
