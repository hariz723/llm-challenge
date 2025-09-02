from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Type


class Settings(BaseSettings):

    # App Config settings
    app_name: str = "Chat Application"
    admin_email: str = "annaduraihari@gmail.com"

    # TODO : Load more env variables here as needed

    # DB Config settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"

    # Security settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    SECRET_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, env_nested_delimiter="__", extra="ignore"
    )

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache(maxsize=1)
def get_settings(settings_class: Type[Settings] = Settings) -> Settings:
    return settings_class()


settings = get_settings()
