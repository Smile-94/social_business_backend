from django.urls import include, path, re_path

from apps.common.views.common_views import custom_404_handler
from config.django.security import security_config

# All routes here are scoped to the active tenant schema
urlpatterns = []

if security_config.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += [*debug_toolbar_urls()]

# # Catch-all 404 for unmatched /api/* tenant routes
# urlpatterns += [
#     re_path(r"^api/.*$", custom_404_handler),
# ]

# handler404 = "apps.common.views.common_views.custom_404_handler"
