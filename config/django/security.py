from typing import Any

from pydantic import Field, SecretStr, computed_field, model_validator

from config.django._base_config import DjangoConfig
from config.environment import EnvironmentChoices, env_config


class SecurityConfig(DjangoConfig):
    """
    Security-critical Django settings loaded via Pydantic.
    Enforces strict cryptographic constraints and production HTTP headers.
    """

    SECRET_KEY: SecretStr = Field(..., min_length=40)

    DEBUG: bool = Field(default=False)

    SECURE_BROWSER_XSS_FILTER: bool = Field(default=True)
    SECURE_CONTENT_TYPE_NOSNIFF: bool = Field(default=True)
    X_FRAME_OPTIONS: str = Field(default="DENY")

    @model_validator(mode="before")
    @classmethod
    def enforce_production_safety(cls, data: Any) -> Any:
        """
        Acts as a final safety net. If the environment is set to PRODUCTION,
        it forcefully overrides the DEBUG flag to False before the model freezes.
        """
        # Ensure we are working with the raw configuration dictionary
        if isinstance(data, dict):
            if env_config.ENVIRONMENT == EnvironmentChoices.PRODUCTION:
                data["DEBUG"] = False

        return data

    @computed_field
    def SECURE_SSL_REDIRECT(self) -> bool:
        return env_config.ENVIRONMENT == EnvironmentChoices.PRODUCTION

    @computed_field
    def SESSION_COOKIE_SECURE(self) -> bool:
        return env_config.ENVIRONMENT == EnvironmentChoices.PRODUCTION

    @computed_field
    def CSRF_COOKIE_SECURE(self) -> bool:
        return env_config.ENVIRONMENT == EnvironmentChoices.PRODUCTION

    @computed_field
    def SECURE_HSTS_SECONDS(self) -> int:
        return 31536000 if env_config.ENVIRONMENT == EnvironmentChoices.PRODUCTION else 0

    @computed_field
    def SECURE_HSTS_INCLUDE_SUBDOMAINS(self) -> bool:
        return env_config.ENVIRONMENT == EnvironmentChoices.PRODUCTION

    @computed_field
    def SECURE_HSTS_PRELOAD(self) -> bool:
        return env_config.ENVIRONMENT == EnvironmentChoices.PRODUCTION

    def as_django_settings(self) -> dict:
        return {
            "SECRET_KEY": self.SECRET_KEY.get_secret_value(),
            "DEBUG": self.DEBUG,
            "SECURE_BROWSER_XSS_FILTER": self.SECURE_BROWSER_XSS_FILTER,
            "SECURE_CONTENT_TYPE_NOSNIFF": self.SECURE_CONTENT_TYPE_NOSNIFF,
            "X_FRAME_OPTIONS": self.X_FRAME_OPTIONS,
            "SECURE_SSL_REDIRECT": self.SECURE_SSL_REDIRECT,
            "SESSION_COOKIE_SECURE": self.SESSION_COOKIE_SECURE,
            "CSRF_COOKIE_SECURE": self.CSRF_COOKIE_SECURE,
            "SECURE_HSTS_SECONDS": self.SECURE_HSTS_SECONDS,
            "SECURE_HSTS_INCLUDE_SUBDOMAINS": self.SECURE_HSTS_INCLUDE_SUBDOMAINS,
            "SECURE_HSTS_PRELOAD": self.SECURE_HSTS_PRELOAD,
        }


security_config = SecurityConfig()
