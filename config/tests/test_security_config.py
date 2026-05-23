from pydantic import ValidationError
import pytest

from config.django.security import SecurityConfig
from config.environment import EnvironmentChoices


# Create our un-frozen dummy object to stand in for env_config
class MockEnvConfig:
    ENVIRONMENT = EnvironmentChoices.PRODUCTION


def test_production_forces_debug_false(monkeypatch):
    """
    CRITICAL SECURITY TEST: Ensure that even if DEBUG=True is explicitly
    set in the production environment variables, the config forces it to False.
    """
    # 1. Arrange: Patch the environment to PRODUCTION
    MockEnvConfig.ENVIRONMENT = EnvironmentChoices.PRODUCTION
    monkeypatch.setattr("config.django.security.env_config", MockEnvConfig)

    # Simulate a compromised or accidental .env configuration
    monkeypatch.setenv("DEBUG", "True")
    monkeypatch.setenv("SECRET_KEY", "super-secret-key-that-is-at-least-40-characters-long-so-it-passes")

    # 2. Act
    config = SecurityConfig()
    django_settings = config.as_django_settings()

    # 3. Assert: The safety net caught it
    assert django_settings["DEBUG"] is False


def test_strict_https_headers_enabled_in_production(monkeypatch):
    """
    Ensure all SSL, HSTS, and Secure Cookie flags are active in Production.
    """
    MockEnvConfig.ENVIRONMENT = EnvironmentChoices.PRODUCTION
    monkeypatch.setattr("config.django.security.env_config", MockEnvConfig)
    monkeypatch.setenv("SECRET_KEY", "super-secret-key-that-is-at-least-40-characters-long-so-it-passes")

    config = SecurityConfig()
    django_settings = config.as_django_settings()

    assert django_settings["SECURE_SSL_REDIRECT"] is True
    assert django_settings["SESSION_COOKIE_SECURE"] is True
    assert django_settings["CSRF_COOKIE_SECURE"] is True
    assert django_settings["SECURE_HSTS_SECONDS"] == 31536000
    assert django_settings["SECURE_HSTS_PRELOAD"] is True


def test_strict_https_headers_disabled_in_local(monkeypatch):
    """
    Ensure SSL/HSTS flags are disabled in local development so
    developers can work via http://localhost without browser errors.
    """
    MockEnvConfig.ENVIRONMENT = EnvironmentChoices.LOCAL
    monkeypatch.setattr("config.django.security.env_config", MockEnvConfig)
    monkeypatch.setenv("SECRET_KEY", "super-secret-key-that-is-at-least-40-characters-long-so-it-passes")

    config = SecurityConfig()
    django_settings = config.as_django_settings()

    assert django_settings["SECURE_SSL_REDIRECT"] is False
    assert django_settings["SESSION_COOKIE_SECURE"] is False
    assert django_settings["SECURE_HSTS_SECONDS"] == 0


def test_secret_key_validation(monkeypatch):
    """
    Ensure the application refuses to start if the SECRET_KEY is missing
    or has weak entropy (less than 40 characters).
    """
    # Test 1: Missing entirely
    monkeypatch.delenv("SECRET_KEY", raising=False)

    with pytest.raises(ValidationError) as exc_info:
        # Pass _env_file=None so Pydantic doesn't secretly
        # read the key back out of your .env.local file on disk!
        SecurityConfig(_env_file=None)

    assert "Field required" in str(exc_info.value)

    # Test 2: Too short (weak entropy)
    # Even with _env_file=None, os.environ (monkeypatch) still works!
    monkeypatch.setenv("SECRET_KEY", "too-short-key")

    with pytest.raises(ValidationError) as exc_info:
        SecurityConfig(_env_file=None)

    assert "at least 40" in str(exc_info.value)
