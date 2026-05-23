from django.contrib import sessions
from pydantic import ValidationError
import pytest

from config.django.sessions import SessionConfig
from config.environment import EnvironmentChoices


# Create our un-frozen dummy object to stand in for env_config
class MockEnvConfig:
    ENVIRONMENT = EnvironmentChoices.PRODUCTION


def test_session_cookie_secure_in_production(monkeypatch):
    """
    CRITICAL SECURITY TEST: Ensure session cookies are locked to HTTPS
    when deployed to Production.
    """
    MockEnvConfig.ENVIRONMENT = EnvironmentChoices.PRODUCTION
    monkeypatch.setattr("config.django.sessions.env_config", MockEnvConfig)

    config = SessionConfig()
    django_settings = config.as_django_settings()

    assert django_settings["SESSION_COOKIE_SECURE"] is True


def test_session_cookie_secure_in_staging(monkeypatch):
    """
    CRITICAL SECURITY TEST: Ensure session cookies are locked to HTTPS
    when deployed to Staging.
    """
    MockEnvConfig.ENVIRONMENT = EnvironmentChoices.STAGING
    monkeypatch.setattr("config.django.sessions.env_config", MockEnvConfig)

    config = SessionConfig()
    django_settings = config.as_django_settings()

    assert django_settings["SESSION_COOKIE_SECURE"] is True


def test_session_cookie_insecure_in_local(monkeypatch):
    """
    Ensure developers can test locally over HTTP without cookies being dropped.
    """
    MockEnvConfig.ENVIRONMENT = EnvironmentChoices.LOCAL
    monkeypatch.setattr("config.django.sessions.env_config", MockEnvConfig)

    config = SessionConfig()
    django_settings = config.as_django_settings()

    assert django_settings["SESSION_COOKIE_SECURE"] is False


def test_session_samesite_validation():
    """
    Ensure the configuration rejects invalid SameSite policies.
    """
    # Test valid override
    config = SessionConfig(SESSION_COOKIE_SAMESITE="Strict")
    assert config.SESSION_COOKIE_SAMESITE == "Strict"

    # Test invalid override (should raise a Pydantic ValidationError)
    with pytest.raises(ValidationError) as exc_info:
        SessionConfig(SESSION_COOKIE_SAMESITE="InvalidPolicy")

    assert "Input should be 'Strict', 'Lax' or 'None'" in str(exc_info.value)


def test_session_cookie_age_validation():
    """
    Ensure the session cookie age cannot be set below the 5-minute (300s) threshold.
    """
    # Test valid short age
    config = SessionConfig(SESSION_COOKIE_AGE=300)
    assert config.SESSION_COOKIE_AGE == 300

    # Test invalid short age (e.g., a dev accidentally puts 60 seconds)
    with pytest.raises(ValidationError) as exc_info:
        SessionConfig(SESSION_COOKIE_AGE=60)

    assert "Input should be greater than or equal to 300" in str(exc_info.value)
