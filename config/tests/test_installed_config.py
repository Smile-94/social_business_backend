import pytest

from config.django.installed_apps import InstalledAppsConfig
from config.environment import EnvironmentChoices


class MockEnvConfig:
    ENVIRONMENT = EnvironmentChoices.PRODUCTION


def test_debug_toolbar_excluded_in_production(monkeypatch):
    """Ensure the debug_toolbar is never loaded in PRODUCTION."""

    # 1. Arrange: Patch the env_config object *inside* the installed_apps module
    MockEnvConfig.ENVIRONMENT = EnvironmentChoices.PRODUCTION
    monkeypatch.setattr("config.django.installed_apps.env_config", MockEnvConfig)

    # 2. Act
    config = InstalledAppsConfig()
    django_settings = config.as_django_settings()

    # 3. Assert
    assert "debug_toolbar" not in django_settings["INSTALLED_APPS"]


def test_debug_toolbar_excluded_in_staging(monkeypatch):
    """Ensure the debug_toolbar is never loaded in STAGING."""

    MockEnvConfig.ENVIRONMENT = EnvironmentChoices.STAGING
    monkeypatch.setattr("config.django.installed_apps.env_config", MockEnvConfig)

    config = InstalledAppsConfig()
    django_settings = config.as_django_settings()

    assert "debug_toolbar" not in django_settings["INSTALLED_APPS"]


def test_debug_toolbar_included_in_local(monkeypatch):
    """Ensure the debug_toolbar is properly injected for LOCAL development."""

    MockEnvConfig.ENVIRONMENT = EnvironmentChoices.LOCAL
    monkeypatch.setattr("config.django.installed_apps.env_config", MockEnvConfig)

    config = InstalledAppsConfig()
    django_settings = config.as_django_settings()

    assert "debug_toolbar" in django_settings["INSTALLED_APPS"]
    assert django_settings["INSTALLED_APPS"][-1] == "debug_toolbar"


def test_installed_apps_loading_order(monkeypatch):
    """Ensure Django core apps load before third-party, and local apps load last."""

    MockEnvConfig.ENVIRONMENT = EnvironmentChoices.PRODUCTION
    monkeypatch.setattr("config.django.installed_apps.env_config", MockEnvConfig)

    config = InstalledAppsConfig()
    apps = config.INSTALLED_APPS

    admin_index = apps.index("django.contrib.admin")
    rest_framework_index = apps.index("rest_framework")
    local_app_index = apps.index("apps.common.apps.CommonConfig")

    assert admin_index < rest_framework_index < local_app_index
