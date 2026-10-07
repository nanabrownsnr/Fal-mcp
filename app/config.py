"""Typed runtime configuration for the Fal MCP service."""

from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    SERVICE_ID: str = "fal_mcp"
    APP_TITLE: str = "Fal MCP"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    PUBLIC_URL: str = "http://localhost:8000"
    ALLOWED_ORIGINS: str = "*"

    MONGODB_URI: str
    DATABASE_NAME: str = "fal_mcp"
    ENCRYPTION_KEY: str

    ACCOUNT_SERVICE_URL: str
    ACCOUNT_SERVICE_JWKS_ENDPOINT: str = "/.well-known/jwks.json"
    ACCOUNT_SERVICE_JWKS_CACHE_TTL: int = Field(default=600, ge=0)
    PERSONA_ID_HEADER: str = "Persona-Id"

    USAGE_REPORT_ENDPOINT: str = ""
    DEFAULT_FAL_MODEL: str = "fal-ai/flux/schnell"
    LICENSE_ENFORCEMENT_ENABLED: bool = False
    LICENSE_KEY: str = ""
    LICENSE_SERVER_BASE_URL: str = ""
    LICENSE_SERVER_JWKS_ENDPOINT: str = "/.well-known/jwks.json"
    LICENSE_SERVER_ACTIVATION_ENDPOINT: str = "/api/v1/activations"

    @model_validator(mode="after")
    def require_license_configuration_when_enabled(self) -> "Settings":
        if self.LICENSE_ENFORCEMENT_ENABLED and not (
            self.LICENSE_KEY and self.LICENSE_SERVER_BASE_URL
        ):
            raise ValueError(
                "LICENSE_KEY and LICENSE_SERVER_BASE_URL are required when license enforcement is enabled"
            )
        return self

    @property
    def account_jwks_url(self) -> str:
        return (
            f"{self.ACCOUNT_SERVICE_URL.rstrip('/')}/"
            f"{self.ACCOUNT_SERVICE_JWKS_ENDPOINT.lstrip('/')}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
