from enum import Enum
from pathlib import Path

from pydantic import Field, SecretStr, computed_field

from config.django._base_config import DjangoConfig
from config.environment import BASE_DIR


class DatabaseEngine(str, Enum):
    """Supported Django database backend identifiers."""

    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    ORACLE = "oracle"
    MSSQL = "mssql"


# Maps our enum values to Django's backend dotted paths.
_ENGINE_MAP: dict[DatabaseEngine, str] = {
    DatabaseEngine.SQLITE: "django.db.backends.sqlite3",
    DatabaseEngine.POSTGRESQL: "django_tenants.postgresql_backend",
    DatabaseEngine.MYSQL: "django.db.backends.mysql",
    DatabaseEngine.ORACLE: "django.db.backends.oracle",
    DatabaseEngine.MSSQL: "django.db.backends.mssql",
}


class DatabaseConfig(DjangoConfig):
    """
    Database connection and pooling settings.

    BASE_DIR is imported directly from config.environment — not from
    base_config — to prevent inter-config coupling between sibling modules.
    """

    DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"

    DATABASE_ENGINE: DatabaseEngine = Field(default=DatabaseEngine.POSTGRESQL)

    DATABASE_HOST: str = Field(default="localhost")
    DATABASE_PORT: int = Field(default=5432)
    DATABASE_NAME: str = Field(default="postgres")
    DATABASE_USER: str = Field(default="postgres")
    DATABASE_PASSWORD: SecretStr | None = Field(default=None, repr=False)

    # Reuse connections for up to 60s; eliminates per-request TCP handshake.
    DATABASE_CONN_MAX_AGE: int = Field(default=60, ge=0)

    # Ping the connection before reuse to detect stale connections in pools.
    DATABASE_CONN_HEALTH_CHECKS: bool = Field(default=True)

    DATABASE_ROUTERS: tuple[str, ...] = ("django_tenants.routers.TenantSyncRouter",)

    @computed_field
    def DATABASES(self) -> dict:
        """Generate the Django DATABASES dictionary for the selected engine."""
        engine = _ENGINE_MAP[self.DATABASE_ENGINE]

        if self.DATABASE_ENGINE == DatabaseEngine.SQLITE:
            print("Using SQLite database")
            return {
                "default": {
                    "ENGINE": engine,
                    "NAME": Path(BASE_DIR) / "db.sqlite3",
                }
            }

        pwd = self.DATABASE_PASSWORD.get_secret_value() if self.DATABASE_PASSWORD else ""

        return {
            "default": {
                "ENGINE": engine,
                "NAME": self.DATABASE_NAME,
                "USER": self.DATABASE_USER,
                "PASSWORD": pwd,
                "HOST": self.DATABASE_HOST,
                "PORT": self.DATABASE_PORT,
                "CONN_MAX_AGE": self.DATABASE_CONN_MAX_AGE,
                "CONN_HEALTH_CHECKS": self.DATABASE_CONN_HEALTH_CHECKS,
            }
        }

    def as_django_settings(self) -> dict:
        return {
            "DEFAULT_AUTO_FIELD": self.DEFAULT_AUTO_FIELD,
            "DATABASES": self.DATABASES,
            "DATABASE_ROUTERS": self.DATABASE_ROUTERS,
        }


database_config = DatabaseConfig()
