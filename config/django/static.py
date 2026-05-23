from pathlib import Path
from typing import Any

from pydantic import Field

from config.django._base_config import DjangoConfig
from config.django.base import base_config


class StaticConfig(DjangoConfig):
    """
    Static and media file configuration loaded via Pydantic.
    Optimized for pure pathlib operations and robust production serving.
    """

    STATIC_URL: str = Field(default="/static/")

    STATIC_ROOT: Path = Field(default=base_config.BASE_DIR / "staticfiles")

    STATICFILES_DIRS: list[Path] = Field(default_factory=lambda: [base_config.BASE_DIR / "static"])

    MEDIA_URL: str = Field(default="/media/")

    MEDIA_ROOT: Path = Field(default=base_config.BASE_DIR / "media")

    STORAGES: dict[str, dict[str, Any]] = Field(
        default={
            "default": {
                "BACKEND": "django.core.files.storage.FileSystemStorage",
            },
            "staticfiles": {
                "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
            },
        }
    )

    def as_django_settings(self) -> dict:
        return {
            "STATIC_URL": self.STATIC_URL,
            "STATIC_ROOT": self.STATIC_ROOT,
            "STATICFILES_DIRS": self.STATICFILES_DIRS,
            "MEDIA_URL": self.MEDIA_URL,
            "MEDIA_ROOT": self.MEDIA_ROOT,
            "STORAGES": self.STORAGES,
        }


# Singleton static/media configuration instance
static_config = StaticConfig()
