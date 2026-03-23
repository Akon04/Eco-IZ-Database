from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://ecoiz:ecoiz@localhost:5432/ecoiz"
    ecoiz_api_host: str = "127.0.0.1"
    ecoiz_api_port: int = 8000
    ecoiz_cors_origins: str = "*"
    openai_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        if self.ecoiz_cors_origins.strip() == "*":
            return ["*"]
        return [item.strip() for item in self.ecoiz_cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
