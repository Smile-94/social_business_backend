import logging

from pydantic_settings import BaseSettings, SettingsConfigDict

from config.environment import env_config

logger = logging.getLogger(__name__)


class DjangoConfig(BaseSettings):
    """
    Abstract base for all Django configuration sections.

    Subclasses MUST implement ``as_django_settings()``.
    Subclasses MUST NOT repeat model_config — it is inherited.
    """

    model_config = SettingsConfigDict(
        env_file=env_config.environment_file,
        extra="ignore",
        frozen=True,
    )
    logger.info(f"Loading config from {env_config.environment_file}")

    def as_django_settings(self) -> dict:
        """
        Return a flat dict of Django-ready settings.

        Contract
        --------
        - Keys must be UPPER_SNAKE_CASE Django setting names.
        - Values must be Django-ready (lists, not tuples; plain str not SecretStr).
        - Non-serialisable callables must live here, not on the model itself.
        - Never expose raw/unparsed values (CSV strings, private fields, etc.).
        """
        raise NotImplementedError(
            f"{type(self).__name__} must implement as_django_settings(). "
            "Every config section must declare its Django settings explicitly."
        )
