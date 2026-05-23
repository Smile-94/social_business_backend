from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from apps.common.views.common_views import custom_404_handler
from config.django.security import security_config

urlpatterns = [
    path("admin/", admin.site.urls),
]

if security_config.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += [
        path("dev/api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path("dev/api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
        path("dev/api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    ]
    # urlpatterns += [*debug_toolbar_urls()]

# SaaS-level API routes (auth, subscriptions, tenant management)
urlpatterns += []

handler404 = "apps.common.views.common_views.custom_404_handler"
