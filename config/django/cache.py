from pydantic import Field, SecretStr, computed_field

from config.django._base_config import DjangoConfig


class CacheConfig(DjangoConfig):
    """Redis connection pool and Django cache settings."""

    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_PASSWORD: SecretStr | None = Field(default=None, repr=False)

    REDIS_DB: int = Field(default=1, ge=0, description="Django cache DB index.")
    REDIS_DB_BROKER: int = Field(default=2, ge=0, description="Celery broker DB index.")
    REDIS_DB_BACKEND: int = Field(default=3, ge=0, description="Celery result backend DB index.")
    REDIS_DB_CHANNEL: int = Field(default=4, ge=0, description="Django Channels layer DB index.")

    CACHES_TIMEOUT: int = Field(default=60)
    SOCKET_CONNECT_TIMEOUT: int = Field(default=5)
    SOCKET_TIMEOUT: int = Field(default=5)
    IGNORE_EXCEPTIONS: bool = Field(default=True)
    RETRY_ON_TIMEOUT: bool = Field(default=False)

    def _build_redis_url(self, db_index: int) -> str:
        """Construct a Redis URL for a given DB index with optional auth."""
        pwd = self.REDIS_PASSWORD.get_secret_value() if self.REDIS_PASSWORD else ""
        auth = f":{pwd}@" if pwd else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{db_index}"

    @property
    def broker_url(self) -> str:
        """Redis URL for the Celery broker."""
        return self._build_redis_url(self.REDIS_DB_BROKER)

    @property
    def backend_url(self) -> str:
        """Redis URL for the Celery result backend."""
        return self._build_redis_url(self.REDIS_DB_BACKEND)

    @property
    def channel_url(self) -> str:
        """Redis URL for the Django Channels layer."""
        return self._build_redis_url(self.REDIS_DB_CHANNEL)

    @computed_field
    def CACHES(self) -> dict:
        """Generate the Django CACHES dictionary."""
        pwd = self.REDIS_PASSWORD.get_secret_value() if self.REDIS_PASSWORD else ""

        options: dict = {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": self.SOCKET_CONNECT_TIMEOUT,
            "SOCKET_TIMEOUT": self.SOCKET_TIMEOUT,
            "IGNORE_EXCEPTIONS": self.IGNORE_EXCEPTIONS,
            "RETRY_ON_TIMEOUT": self.RETRY_ON_TIMEOUT,
        }

        if pwd:
            options["PASSWORD"] = pwd

        return {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": self._build_redis_url(self.REDIS_DB),
                "OPTIONS": options,
                "TIMEOUT": self.CACHES_TIMEOUT,
            }
        }

    def as_django_settings(self) -> dict:
        return {"CACHES": self.CACHES}


cache_config = CacheConfig()
