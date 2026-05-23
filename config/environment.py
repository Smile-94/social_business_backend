from enum import Enum
from pathlib import Path

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class EnvironmentChoices(Enum):
    """
    Strict enumeration of permitted runtime environments.

    Using an Enum prevents silent, typo-driven configuration failures
    (e.g., starting up with 'prod' instead of 'production', causing it to
    silently fall back to default settings).
    """

    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class EnvironmentConfig(BaseSettings):
    """
    Core environment state manager and file router.

    Responsibility (SRP):
        Determine the active runtime environment and establish the path
        to the corresponding secrets file.

    Constraint:
        This class must NOT load databases, API keys, or Django-specific
        settings. It strictly routes the environment state. Downstream classes
        (like `DatabaseSettings` or `DjangoSettings`) will use the output of this class.
    """

    # Frozen state guarantees the environment identity is immutable during runtime,
    # preventing accidental mutations that could cross-pollinate environment data.
    ENVIRONMENT: EnvironmentChoices = Field(
        default=EnvironmentChoices.LOCAL,
        frozen=True,
        description="The active deployment environment. Injected via OS or base .env",
    )

    @computed_field
    def environment_file(self) -> str:
        """
        Derives the absolute path to the target environment secrets file.

        Returns:
            str: Absolute path string (e.g., '/app/config/_environment/.env.production')

        Note:
            Downstream configuration classes should use this path in their
            `env_file` definition to load their specific keys.
        """
        env_path = BASE_DIR / "_environment" / f".env.{self.ENVIRONMENT.value}"
        return str(env_path)

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / "_environment" / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


env_config = EnvironmentConfig()
