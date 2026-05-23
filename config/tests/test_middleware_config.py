import pytest

from config.django.middleware import MiddlewareConfig
from config.environment import EnvironmentChoices


class MockEnvConfig:
    ENVIRONMENT = EnvironmentChoices.PRODUCTION


def test_debug_toolbar_middleware_excluded_in_production(monkeypatch):
    """
    CRITICAL: Ensure the debug_toolbar middleware is never loaded
    when the environment is set to PRODUCTION to prevent startup crashes.
    """
    MockEnvConfig.ENVIRONMENT = EnvironmentChoices.PRODUCTION
    monkeypatch.setattr("config.django.middleware.env_config", MockEnvConfig)

    config = MiddlewareConfig()
    django_settings = config.as_django_settings()

    assert "debug_toolbar.middleware.DebugToolbarMiddleware" not in django_settings["MIDDLEWARE"]


def test_debug_toolbar_middleware_included_in_local(monkeypatch):
    """
    Ensure the debug_toolbar middleware is properly injected for local development.
    """
    MockEnvConfig.ENVIRONMENT = EnvironmentChoices.LOCAL
    monkeypatch.setattr("config.django.middleware.env_config", MockEnvConfig)

    config = MiddlewareConfig()
    django_settings = config.as_django_settings()

    assert "debug_toolbar.middleware.DebugToolbarMiddleware" in django_settings["MIDDLEWARE"]
    # Ensure it's loaded early in the stack
    assert django_settings["MIDDLEWARE"][0] == "debug_toolbar.middleware.DebugToolbarMiddleware"


def test_middleware_order_is_maintained(monkeypatch):
    """
    Ensure Core, Third-Party, and Custom middleware are concatenated in the correct order.
    """
    MockEnvConfig.ENVIRONMENT = EnvironmentChoices.PRODUCTION
    monkeypatch.setattr("config.django.middleware.env_config", MockEnvConfig)

    config = MiddlewareConfig()
    middleware = config.MIDDLEWARE

    core_index = middleware.index("django.contrib.auth.middleware.AuthenticationMiddleware")
    third_party_index = middleware.index("whitenoise.middleware.WhiteNoiseMiddleware")
    custom_index = middleware.index("apps.common.middleware.custom_middleware.RequestLoggingMiddleware")

    assert core_index < third_party_index < custom_index
