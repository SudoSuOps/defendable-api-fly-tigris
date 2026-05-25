from __future__ import annotations

from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="development", alias="APP_ENV")
    app_name: str = Field(default="DefendableAPI", alias="APP_NAME")
    port: int = Field(default=8080, alias="PORT")

    database_url: Optional[str] = Field(default=None, alias="DATABASE_URL")

    aws_endpoint_url_s3: str = Field(
        default="https://fly.storage.tigris.dev", alias="AWS_ENDPOINT_URL_S3"
    )
    aws_access_key_id: Optional[str] = Field(default=None, alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, alias="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="auto", alias="AWS_REGION")
    tigris_bucket: str = Field(default="defendable-ledger", alias="TIGRIS_BUCKET")

    api_bearer_token: Optional[str] = Field(default=None, alias="API_BEARER_TOKEN")

    cors_origins_raw: str = Field(default="", alias="CORS_ORIGINS")

    @property
    def cors_origins(self) -> List[str]:
        if not self.cors_origins_raw:
            return ["*"]
        return [o.strip() for o in self.cors_origins_raw.split(",") if o.strip()]

    @property
    def auth_required(self) -> bool:
        return bool(self.api_bearer_token)


@lru_cache(maxsize=1)
def settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
