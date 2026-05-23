import pytest

from config.django.cache import CacheConfig


def test_redis_urls_without_password(monkeypatch):
    """Ensure URLs are constructed cleanly when no password is set."""
    # Ensure no password is set in the environment
    monkeypatch.delenv("REDIS_PASSWORD", raising=False)
    monkeypatch.setenv("REDIS_HOST", "cache-server")

    config = CacheConfig()

    # Check that no stray auth formatting (like ':@') is in the URL
    assert config._build_redis_url(1) == "redis://cache-server:6379/1"

    # Ensure the different DB properties map to the correct indexes
    assert config.broker_url == "redis://cache-server:6379/2"
    assert config.backend_url == "redis://cache-server:6379/3"
    assert config.channel_url == "redis://cache-server:6379/4"

    # Ensure PASSWORD key is entirely absent from options
    django_settings = config.as_django_settings()
    assert "PASSWORD" not in django_settings["CACHES"]["default"]["OPTIONS"]


def test_redis_urls_with_password(monkeypatch):
    """Ensure URLs and CACHE options correctly include the password when provided."""
    monkeypatch.setenv("REDIS_PASSWORD", "super-secret-redis-key")
    monkeypatch.setenv("REDIS_HOST", "10.0.0.5")

    config = CacheConfig()

    # Check that the URL includes the auth string
    assert config.broker_url == "redis://:super-secret-redis-key@10.0.0.5:6379/2"

    # Ensure the PASSWORD key was injected into the cache OPTIONS dictionary
    django_settings = config.as_django_settings()
    assert django_settings["CACHES"]["default"]["OPTIONS"]["PASSWORD"] == "super-secret-redis-key"
