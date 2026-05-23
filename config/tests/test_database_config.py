from pydantic import ValidationError
import pytest

from config.django.database import DatabaseConfig
from config.environment import BASE_DIR

# ------------------------------------------------------------------------
# Database Configuration Tests
# ------------------------------------------------------------------------


def test_database_config_sqlite_branch(monkeypatch):
    """
    Ensure that when SQLite is selected, the configuration ignores network
    credentials and correctly constructs the file path based on BASE_DIR.
    """
    monkeypatch.setenv("DATABASE_ENGINE", "sqlite")
    # Set network variables to prove they are ignored
    monkeypatch.setenv("DATABASE_HOST", "10.0.0.1")

    config = DatabaseConfig()
    django_settings = config.as_django_settings()
    db_dict = django_settings["DATABASES"]["default"]

    assert db_dict["ENGINE"] == "django.db.backends.sqlite3"
    assert db_dict["NAME"] == BASE_DIR / "db.sqlite3"

    # Ensure network keys DO NOT exist in the SQLite dictionary
    assert "HOST" not in db_dict
    assert "USER" not in db_dict


def test_database_config_postgres_with_password(monkeypatch):
    """
    Ensure network databases (like Postgres) correctly unwrap the SecretStr
    password and assemble the full connection dictionary.
    """
    monkeypatch.setenv("DATABASE_ENGINE", "postgresql")
    monkeypatch.setenv("DATABASE_HOST", "db.production.internal")
    monkeypatch.setenv("DATABASE_PORT", "5432")
    monkeypatch.setenv("DATABASE_NAME", "my_prod_db")
    monkeypatch.setenv("DATABASE_USER", "db_admin")
    monkeypatch.setenv("DATABASE_PASSWORD", "super-secret-db-password")

    config = DatabaseConfig()
    django_settings = config.as_django_settings()
    db_dict = django_settings["DATABASES"]["default"]

    assert db_dict["ENGINE"] == "django.db.backends.postgresql"
    assert db_dict["HOST"] == "db.production.internal"
    assert db_dict["PORT"] == 5432
    assert db_dict["NAME"] == "my_prod_db"
    assert db_dict["USER"] == "db_admin"
    # Ensure the password was correctly unwrapped from SecretStr
    assert db_dict["PASSWORD"] == "super-secret-db-password"
    assert db_dict["CONN_MAX_AGE"] == 60


def test_database_config_network_db_without_password(monkeypatch):
    """
    Ensure the configuration handles empty/missing passwords gracefully
    without throwing a NoneType error on SecretStr.
    """
    monkeypatch.setenv("DATABASE_ENGINE", "postgresql")
    monkeypatch.delenv("DATABASE_PASSWORD", raising=False)

    config = DatabaseConfig()
    django_settings = config.as_django_settings()

    # It should safely fall back to an empty string
    assert django_settings["DATABASES"]["default"]["PASSWORD"] == ""


def test_database_config_rejects_invalid_engine(monkeypatch):
    """
    CRITICAL: Ensure Pydantic's Enum validation blocks invalid database strings
    before Django attempts to boot with a bad backend.
    """
    # Simulate a typo in the .env file
    monkeypatch.setenv("DATABASE_ENGINE", "postgres")  # Should be 'postgresql'

    with pytest.raises(ValidationError) as exc_info:
        DatabaseConfig()

    assert "Input should be" in str(exc_info.value)
    assert "postgresql" in str(exc_info.value)
