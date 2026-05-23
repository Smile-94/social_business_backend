from pydantic import Field, computed_field

from config.django._base_config import DjangoConfig
from config.environment import EnvironmentChoices, env_config

_DEFAULT_LOG_LEVEL = "DEBUG" if env_config.ENVIRONMENT in (EnvironmentChoices.LOCAL, EnvironmentChoices.DEVELOPMENT) else "INFO"


class LoggingConfig(DjangoConfig):
    """
    Environment-aware logging settings.

    LOG_LEVEL defaults to DEBUG in local/dev and INFO in staging/production,
    but can always be overridden via the LOG_LEVEL environment variable.
    """

    LOG_LEVEL: str = Field(default=_DEFAULT_LOG_LEVEL)

    @computed_field
    def LOGGING(self) -> dict:
        """Generate the Django LOGGING dictionary."""

        db_level = "DEBUG" if self.LOG_LEVEL == "DEBUG" else "WARNING"

        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "verbose": {
                    "format": "{levelname} {asctime} [{module}:{lineno}] {message}",
                    "style": "{",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {"class": "logging.StreamHandler", "formatter": "verbose", "level": self.LOG_LEVEL},
            },
            "root": {"handlers": ["console"], "level": self.LOG_LEVEL},
            "loggers": {
                "django": {"handlers": ["console"], "level": self.LOG_LEVEL, "propagate": False},
                "django.utils.autoreload": {"handlers": ["console"], "level": "INFO", "propagate": False},
                "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": False},
                # "django.db.backends": {"handlers": ["console"], "level": db_level, "propagate": False},
                "django.db.backends": {"handlers": ["console"], "level": "INFO", "propagate": False},
                "celery": {"handlers": ["console"], "level": self.LOG_LEVEL, "propagate": False},
            },
        }

    def as_django_settings(self) -> dict:
        return {"LOGGING": self.LOGGING}


logging_config = LoggingConfig()
