from typing import Any

from pydantic import Field, SecretStr

from config.django._base_config import DjangoConfig


class AuthConfig(DjangoConfig):
    """
    Authentication settings: user model, token lifecycle, backends,
    and password validation policy.
    """

    AUTH_USER_MODEL: str = Field(
        default="user.User",
        description="Custom user model. Must match the app label exactly.",
    )

    TOKEN_SECRET_KEY: SecretStr = Field(
        ...,
        min_length=32,
        description="Cryptographic key for JWT/token generation.",
    )

    ACCESS_TOKEN_TTL: int = Field(default=3600, ge=1)
    REFRESH_TOKEN_TTL: int = Field(default=1_209_600, ge=1)

    AUTHENTICATION_BACKENDS: list[str] = [
        "django.contrib.auth.backends.ModelBackend",
    ]

    AUTH_PASSWORD_VALIDATORS: list[dict[str, Any]] = [
        {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
        {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
        {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
        {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
        # {"NAME": "apps.common.helper_class.password.StrongPasswordValidator", "OPTIONS": {"min_length": 8}},
    ]

    def as_django_settings(self) -> dict:
        return {
            "AUTH_USER_MODEL": self.AUTH_USER_MODEL,
            "TOKEN_SECRET_KEY": self.TOKEN_SECRET_KEY.get_secret_value(),
            "ACCESS_TOKEN_TTL": self.ACCESS_TOKEN_TTL,
            "REFRESH_TOKEN_TTL": self.REFRESH_TOKEN_TTL,
            "AUTHENTICATION_BACKENDS": self.AUTHENTICATION_BACKENDS,
            "AUTH_PASSWORD_VALIDATORS": self.AUTH_PASSWORD_VALIDATORS,
        }


auth_config = AuthConfig()
