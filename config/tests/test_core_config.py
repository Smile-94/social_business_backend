from pydantic import ValidationError
import pytest

from config.django.base import CoreConfig, _show_debug_toolbar, is_valid_ip, split_and_clean


# <<------------------------------ Utility Function Tests ------------------------------>>
def test_split_and_clean():
    """Ensure comma-separated strings are parsed, stripped, and drop empty items."""
    raw_string = " localhost,  127.0.0.1 ,, example.com  "
    result = split_and_clean(raw_string)
    assert result == ["localhost", "127.0.0.1", "example.com"]


def test_is_valid_ip():
    """Ensure IP validation correctly identifies IPv4, IPv6, and non-IPs."""
    assert is_valid_ip("127.0.0.1") is True
    assert is_valid_ip("::1") is True
    assert is_valid_ip("localhost") is False
    assert is_valid_ip("example.com") is False


# <<------------------------------ CoreConfig Tests ------------------------------>>
def test_core_config_rejects_missing_url_scheme(monkeypatch):
    """
    CRITICAL: Ensure Pydantic raises a ValidationError if a CORS or CSRF
    origin lacks an http:// or https:// scheme.
    """
    monkeypatch.setenv("TRUSTED_ORIGIN", "https://example.com, bad-origin.com")

    with pytest.raises(ValidationError) as exc_info:
        CoreConfig()

    assert "must start with 'http://' or 'https://'" in str(exc_info.value)


def test_core_config_derives_internal_ips(monkeypatch):
    """
    Ensure SERVER_NAME populates ALLOWED_HOSTS fully, but only extracts
    valid IPs into INTERNAL_IPS for the debug toolbar.
    """
    monkeypatch.setenv("SERVER_NAME", "localhost, 127.0.0.1, api.mywebsite.com, 192.168.1.5")
    monkeypatch.setenv("TRUSTED_ORIGIN", "https://api.mywebsite.com")

    config = CoreConfig()
    django_settings = config.as_django_settings()

    assert django_settings["ALLOWED_HOSTS"] == ["localhost", "127.0.0.1", "api.mywebsite.com", "192.168.1.5"]

    # INTERNAL_IPS should only have the actual IP addresses
    assert django_settings["INTERNAL_IPS"] == ["127.0.0.1", "192.168.1.5"]


def test_debug_toolbar_callback():
    """Ensure the debug toolbar is hidden for API routes to prevent JSON corruption."""

    class MockRequest:
        def __init__(self, path):
            self.path = path

    # Should be True for standard views
    assert _show_debug_toolbar(MockRequest("/admin/users/")) is True
    assert _show_debug_toolbar(MockRequest("/dashboard/")) is True

    # Should be False for API endpoints
    assert _show_debug_toolbar(MockRequest("/api/v1/users/")) is False
