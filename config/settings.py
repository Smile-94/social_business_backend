"""
settings.py
===========
Django settings entry point.

This file contains NO logic and NO field unpacking.
Each config module owns its own settings dict via ``as_django_settings()``.
Adding a new setting only requires changing the relevant config class — never this file.

Load order matters: later configs overwrite earlier ones on key collision.
The order below is intentional (base → security → feature configs).
"""

from config.django.authentication import auth_config
from config.django.base import base_config
from config.django.cache import cache_config
from config.django.celery import celery_config
from config.django.channel import channel_config
from config.django.database import database_config
from config.django.documentation import documentation_config
from config.django.installed_apps import installed_apps_config
from config.django.jwt import jwt_config
from config.django.logging import logging_config
from config.django.middleware import middleware_config
from config.django.rest_framework import drf_config
from config.django.security import security_config
from config.django.sessions import session_config
from config.django.static import static_config
from config.django.templates import template_config
from config.django.tenant import tenant_config
from config.django.time_zone import time_zone_config

# ------------------------------------------------------------------------------
# Apply all config sections in dependency order.
# Each as_django_settings() returns a flat dict of Django-ready settings.
# ------------------------------------------------------------------------------
_configs = [
    base_config,
    security_config,
    installed_apps_config,
    middleware_config,
    template_config,
    database_config,
    auth_config,
    time_zone_config,
    static_config,
    drf_config,
    cache_config,
    session_config,
    documentation_config,
    logging_config,
    celery_config,
    channel_config,
    tenant_config,
    jwt_config,
]

for _config in _configs:
    globals().update(_config.as_django_settings())
