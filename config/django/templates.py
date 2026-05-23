from pathlib import Path
from typing import Any

from pydantic import Field, computed_field

from config.django._base_config import DjangoConfig
from config.django.base import base_config


class TemplateConfig(DjangoConfig):
    """
    Django template engine configuration loaded via Pydantic.
    Optimized for project-level template resolution and environment-aware caching.
    """

    TEMPLATES_DIR: Path = Field(default=base_config.BASE_DIR / "templates")

    @computed_field
    def TEMPLATES(self) -> list[dict[str, Any]]:
        """
        Assembles the final TEMPLATES list for Django.
        Uses @computed_field to maintain immutability and state consistency.
        """
        return [
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [self.TEMPLATES_DIR],
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.debug",
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ],
                },
            }
        ]

    def as_django_settings(self) -> dict:
        return {
            "TEMPLATES": self.TEMPLATES,
        }


template_config = TemplateConfig()
