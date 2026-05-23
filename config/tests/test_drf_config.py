import pytest

from config.django.rest_framework import RestFrameworkConfig
from config.environment import EnvironmentChoices


# Create our un-frozen dummy object to stand in for env_config
class MockEnvConfig:
    ENVIRONMENT = EnvironmentChoices.PRODUCTION


def test_drf_secure_by_default_in_production(monkeypatch):
    """
    CRITICAL SECURITY TEST: Ensure that in Production, the API defaults to
    requiring authentication and disables the HTML Browsable API.
    """
    # 1. Arrange: Patch the env_config object inside the rest_framework module
    MockEnvConfig.ENVIRONMENT = EnvironmentChoices.PRODUCTION
    monkeypatch.setattr("config.django.rest_framework.env_config", MockEnvConfig)

    # 2. Act
    config = RestFrameworkConfig()
    drf_settings = config.as_django_settings()["REST_FRAMEWORK"]

    # 3. Assert
    assert drf_settings["DEFAULT_PERMISSION_CLASSES"] == ["rest_framework.permissions.IsAuthenticated"]
    assert "rest_framework.renderers.BrowsableAPIRenderer" not in drf_settings["DEFAULT_RENDERER_CLASSES"]
    assert "rest_framework.renderers.JSONRenderer" in drf_settings["DEFAULT_RENDERER_CLASSES"]


def test_drf_allows_browsable_api_in_local(monkeypatch):
    """
    Ensure local development remains easy by allowing anonymous access by default
    and enabling the interactive Browsable API renderer.
    """
    MockEnvConfig.ENVIRONMENT = EnvironmentChoices.LOCAL
    monkeypatch.setattr("config.django.rest_framework.env_config", MockEnvConfig)

    config = RestFrameworkConfig()
    drf_settings = config.as_django_settings()["REST_FRAMEWORK"]

    assert drf_settings["DEFAULT_PERMISSION_CLASSES"] == ["rest_framework.permissions.AllowAny"]
    assert "rest_framework.renderers.BrowsableAPIRenderer" in drf_settings["DEFAULT_RENDERER_CLASSES"]
