import ipaddress
from pathlib import Path

from corsheaders.defaults import default_headers
from pydantic import AliasChoices, Field, field_validator, model_validator

from config.django._base_config import DjangoConfig
from config.environment import BASE_DIR, env_config


def split_and_clean(value: str) -> list[str]:
    """Split a comma-separated string, stripping whitespace and empty entries."""
    return [item.strip() for item in value.split(",") if item.strip()]


def is_valid_ip(value: str) -> bool:
    """Return True if *value* is a valid IPv4 or IPv6 address."""
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def _show_debug_toolbar(request) -> bool:
    return not request.path.startswith("/api/")


class CoreConfig(DjangoConfig):
    """
    Core project configuration.

    Raw env vars (SERVER_NAME, TRUSTED_ORIGIN, CORS_ALLOWED_ORIGINS_RAW)
    are CSV strings parsed and validated into Django-ready tuples.
    Callers should consume settings via ``as_django_settings()``.
    """

    BASE_DIR: Path = Field(default=BASE_DIR)

    SERVER_NAME: str = Field(
        default="",
        validation_alias=AliasChoices("SERVER_NAME"),
        description="Comma-separated hostnames and IP addresses.",
    )
    TRUSTED_ORIGIN: str = Field(
        default="",
        validation_alias=AliasChoices("TRUSTED_ORIGIN"),
        description="Comma-separated CSRF-trusted origins (must include scheme).",
    )
    CORS_ALLOWED_ORIGINS_RAW: str = Field(
        default="http://localhost:3000",
        validation_alias=AliasChoices("CORS_ALLOWED_ORIGINS_RAW"),
        description="Comma-separated CORS allowed origins.",
    )

    ASGI_APPLICATION: str = "config.asgi.application"
    ROOT_URLCONF: str = "config.urls.public_urls"
    PUBLIC_SCHEMA_URLCONF: str = "config.urls.public_urls"
    TENANT_URLCONF: str = "config.urls.tenant_urls"
    PUBLIC_SCHEMA_NAME: str = "public"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_HEADERS: tuple[str, ...] = tuple(default_headers) + (
        "x-device-id",
        "x-browser-fingerprint",
    )

    ALLOWED_HOSTS: tuple[str, ...] = ()
    INTERNAL_IPS: tuple[str, ...] = ()
    CSRF_TRUSTED_ORIGINS: tuple[str, ...] = ()
    CORS_ALLOWED_ORIGINS: tuple[str, ...] = ()

    @field_validator("TRUSTED_ORIGIN", "CORS_ALLOWED_ORIGINS_RAW", mode="before")
    @classmethod
    def require_scheme(cls, value: str, info) -> str:
        """Every origin must carry an explicit http:// or https:// scheme."""
        for origin in split_and_clean(value):
            if not origin.startswith(("http://", "https://")):
                raise ValueError(f"{info.field_name}: {origin!r} must start with 'http://' or 'https://'.")
        return value

    @model_validator(mode="after")
    def derive_security_lists(self) -> "CoreConfig":
        """Parse raw CSV env vars into Django-ready tuples in one DRY pass."""
        _set = object.__setattr__  # required because model is frozen

        allowed = tuple(split_and_clean(self.SERVER_NAME))
        _set(self, "ALLOWED_HOSTS", allowed)
        _set(self, "INTERNAL_IPS", tuple(h for h in allowed if is_valid_ip(h)))
        _set(self, "CSRF_TRUSTED_ORIGINS", tuple(split_and_clean(self.TRUSTED_ORIGIN)))
        _set(self, "CORS_ALLOWED_ORIGINS", tuple(split_and_clean(self.CORS_ALLOWED_ORIGINS_RAW)))

        return self

    def as_django_settings(self) -> dict:
        return {
            "BASE_DIR": self.BASE_DIR,
            "ALLOWED_HOSTS": list(self.ALLOWED_HOSTS),
            "INTERNAL_IPS": list(self.INTERNAL_IPS),
            "CSRF_TRUSTED_ORIGINS": list(self.CSRF_TRUSTED_ORIGINS),
            "CORS_ALLOWED_ORIGINS": list(self.CORS_ALLOWED_ORIGINS),
            "CORS_ALLOW_CREDENTIALS": self.CORS_ALLOW_CREDENTIALS,
            "CORS_ALLOW_HEADERS": list(self.CORS_ALLOW_HEADERS),
            "ASGI_APPLICATION": self.ASGI_APPLICATION,
            "ROOT_URLCONF": self.ROOT_URLCONF,
            "PUBLIC_SCHEMA_URLCONF": self.PUBLIC_SCHEMA_URLCONF,
            "TENANT_URLCONF": self.TENANT_URLCONF,
            "PUBLIC_SCHEMA_NAME": self.PUBLIC_SCHEMA_NAME,
            "DEBUG_TOOLBAR_CONFIG": {"SHOW_TOOLBAR_CALLBACK": _show_debug_toolbar},
        }


base_config = CoreConfig()
