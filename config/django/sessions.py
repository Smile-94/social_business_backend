from typing import Literal

from pydantic import Field, computed_field

from config.django._base_config import DjangoConfig
from config.environment import EnvironmentChoices, env_config


class SessionConfig(DjangoConfig):
    """
    Django session configuration loaded via Pydantic.
    Enforces secure, cache-backed session management by default.
    """

    SESSION_ENGINE: str = Field(default="django.contrib.sessions.backends.cache")
    SESSION_CACHE_ALIAS: str = Field(default="default")

    SESSION_COOKIE_HTTPONLY: bool = Field(default=True)

    SESSION_COOKIE_SAMESITE: Literal["Strict", "Lax", "None"] = Field(default="Lax")

    SESSION_EXPIRE_AT_BROWSER_CLOSE: bool = Field(default=False)

    SESSION_COOKIE_AGE: int = Field(default=86400, ge=300)

    SESSION_SAVE_EVERY_REQUEST: bool = Field(default=False)

    @computed_field
    def SESSION_COOKIE_SECURE(self) -> bool:
        """
        Strictly enforces HTTPS-only cookies in production and staging environments,
        preventing accidental downgrade attacks or misconfigurations in the .env file.
        """
        return env_config.ENVIRONMENT in (
            EnvironmentChoices.PRODUCTION,
            EnvironmentChoices.STAGING,
        )

    def as_django_settings(self) -> dict:
        return {
            "SESSION_ENGINE": self.SESSION_ENGINE,
            "SESSION_CACHE_ALIAS": self.SESSION_CACHE_ALIAS,
            "SESSION_COOKIE_HTTPONLY": self.SESSION_COOKIE_HTTPONLY,
            "SESSION_COOKIE_SAMESITE": self.SESSION_COOKIE_SAMESITE,
            "SESSION_EXPIRE_AT_BROWSER_CLOSE": self.SESSION_EXPIRE_AT_BROWSER_CLOSE,
            "SESSION_COOKIE_AGE": self.SESSION_COOKIE_AGE,
            "SESSION_SAVE_EVERY_REQUEST": self.SESSION_SAVE_EVERY_REQUEST,
            "SESSION_COOKIE_SECURE": self.SESSION_COOKIE_SECURE,
        }


session_config = SessionConfig()
