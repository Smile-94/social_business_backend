from pydantic import Field

from config.django._base_config import DjangoConfig
from config.django.cache import cache_config


class CeleryConfig(DjangoConfig):
    """Celery worker, serialisation, and reliability settings."""

    CELERY_BROKER_URL: str = Field(default_factory=lambda: cache_config.broker_url)
    CELERY_RESULT_BACKEND: str = Field(default_factory=lambda: cache_config.backend_url)

    CELERY_ACCEPT_CONTENT: list[str] = ["json"]
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"

    CELERY_ENABLE_UTC: bool = True
    CELERY_TIMEZONE: str = "UTC"

    CELERY_TASK_ACKS_LATE: bool = True
    CELERY_TASK_REJECT_ON_WORKER_LOST: bool = True
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP: bool = True

    CELERY_WORKER_PREFETCH_MULTIPLIER: int = 1

    def as_django_settings(self) -> dict:
        return {
            "CELERY_BROKER_URL": self.CELERY_BROKER_URL,
            "CELERY_RESULT_BACKEND": self.CELERY_RESULT_BACKEND,
            "CELERY_ACCEPT_CONTENT": self.CELERY_ACCEPT_CONTENT,
            "CELERY_TASK_SERIALIZER": self.CELERY_TASK_SERIALIZER,
            "CELERY_RESULT_SERIALIZER": self.CELERY_RESULT_SERIALIZER,
            "CELERY_ENABLE_UTC": self.CELERY_ENABLE_UTC,
            "CELERY_TIMEZONE": self.CELERY_TIMEZONE,
            "CELERY_TASK_ACKS_LATE": self.CELERY_TASK_ACKS_LATE,
            "CELERY_TASK_REJECT_ON_WORKER_LOST": self.CELERY_TASK_REJECT_ON_WORKER_LOST,
            "CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP": self.CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP,
            "CELERY_WORKER_PREFETCH_MULTIPLIER": self.CELERY_WORKER_PREFETCH_MULTIPLIER,
        }


celery_config = CeleryConfig()
