"""For core settings from ENV."""

import functools
import pathlib

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Project settings."""

    BASE_DIR: pathlib.Path = pathlib.Path(__file__).resolve().parent.parent
    ENVIRONMENT: str = "local"

    CORS_ALLOW_ORIGIN_LIST: str = "http://localhost:8000"

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "base_fastapi_project"
    POSTGRES_PASSWORD: str = "base_fastapi_project"
    POSTGRES_DB: str = "base_fastapi_project"

    REDIS_DSN: str = "redis://localhost:6379"

    @property
    def cors_allow_origins(self) -> list[str]:
        return self.CORS_ALLOW_ORIGIN_LIST.split("&")

    @property
    def postgres_dsn(self) -> str:
        database = self.POSTGRES_DB if self.ENVIRONMENT != "test" else f"{self.POSTGRES_DB}_test"
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{database}"
        )


@functools.lru_cache
def settings() -> Settings:
    return Settings()
