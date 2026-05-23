import pytest

from config.django.cache import cache_config
from config.django.channel import ChannelConfig

# ------------------------------------------------------------------------
# Channel Configuration Tests
# ------------------------------------------------------------------------


def test_channel_layers_integration_with_cache(monkeypatch):
    """
    Ensure ChannelConfig correctly requests the channel_url from CacheConfig
    and structures the dictionary properly for Django Channels.
    """
    # 1. Arrange: Mock the cache_config property to isolate this test
    # from the actual CacheConfig environment variables.
    mock_redis_url = "redis://test-redis-server:6379/99"
    monkeypatch.setattr(type(cache_config), "channel_url", mock_redis_url)

    # Instantiate ChannelConfig with custom values to ensure they pass through
    config = ChannelConfig(CHANNEL_CAPACITY=5000, CHANNEL_EXPIRY=30)

    # 2. Act: Generate the Django settings dictionary
    django_settings = config.as_django_settings()
    layer_config = django_settings["CHANNEL_LAYERS"]["default"]["CONFIG"]

    # 3. Assert: Verify cross-module injection and dictionary structure
    assert layer_config["hosts"] == [mock_redis_url]
    assert layer_config["capacity"] == 5000
    assert layer_config["expiry"] == 30
    assert django_settings["CHANNEL_LAYERS"]["default"]["BACKEND"] == "channels_redis.core.RedisChannelLayer"
