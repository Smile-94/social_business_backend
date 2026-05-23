from pathlib import Path

import pytest

from config.django.base import base_config

# Adjust the import paths based on your project structure
from config.django.templates import TemplateConfig

#


def test_template_directory_resolution(monkeypatch):
    """
    Ensure the TEMPLATES_DIR correctly resolves relative to the base configuration,
    and allows for custom directory overrides.
    """
    # Test default behavior
    config = TemplateConfig()
    assert config.TEMPLATES_DIR == base_config.BASE_DIR / "templates"

    # Test overriding the default path (e.g., if a dev wants to point to a custom theme folder)
    custom_path = Path("/templates/custom_templates")
    custom_config = TemplateConfig(TEMPLATES_DIR=custom_path)
    assert custom_config.TEMPLATES_DIR == custom_path


def test_django_templates_dictionary_schema():
    """
    CRITICAL SCHEMA TEST: Django is highly strict about the structure of the
    TEMPLATES setting. Ensure the dictionary keys and required values are perfectly formed.
    """
    config = TemplateConfig()
    django_settings = config.as_django_settings()

    # 1. It must be a list containing dictionaries
    templates_list = django_settings["TEMPLATES"]
    assert isinstance(templates_list, list)
    assert len(templates_list) == 1

    template_dict = templates_list[0]

    # 2. Check strict Django keys
    assert template_dict["BACKEND"] == "django.template.backends.django.DjangoTemplates"
    assert template_dict["APP_DIRS"] is True

    # 3. Ensure our custom directory made it into the DIRS list
    assert config.TEMPLATES_DIR in template_dict["DIRS"]

    # 4. Verify context processors exist (without hardcoding the whole list, just check a few core ones)
    context_processors = template_dict["OPTIONS"]["context_processors"]
    assert "django.template.context_processors.request" in context_processors
    assert "django.contrib.auth.context_processors.auth" in context_processors
