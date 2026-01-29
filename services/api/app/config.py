from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "dev"
    database_url: str = "postgresql+psycopg://autopilot:autopilot@localhost:5432/autopilot"
    redis_url: str = "redis://localhost:6379/0"
    scheduler_url: str = "http://localhost:8001"

    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str | None = None

    token_encryption_key: str = "CHANGE_ME"

settings = Settings()
