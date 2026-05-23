from typing import Any

from pydantic import Field, computed_field

from config.django._base_config import DjangoConfig
from config.django.cache import cache_config


class ChannelConfig(DjangoConfig):
    """Django Channels Redis layer settings."""

    CHANNEL_CAPACITY: int = Field(default=1500, ge=1)

    CHANNEL_EXPIRY: int = Field(default=10, ge=1)

    @computed_field
    def CHANNEL_LAYERS(self) -> dict[str, dict[str, Any]]:
        """
        Generate the Django CHANNEL_LAYERS dictionary.

        Uses cache_config.channel_url (a public property) rather than the
        previously used cache_config._build_redis_url(0) which breached
        encapsulation by calling a private method across module boundaries.
        """
        return {
            "default": {
                "BACKEND": "channels_redis.core.RedisChannelLayer",
                "CONFIG": {
                    "hosts": [cache_config.channel_url],
                    "capacity": self.CHANNEL_CAPACITY,
                    "expiry": self.CHANNEL_EXPIRY,
                },
            }
        }

    def as_django_settings(self) -> dict:
        return {"CHANNEL_LAYERS": self.CHANNEL_LAYERS}


channel_config = ChannelConfig()
