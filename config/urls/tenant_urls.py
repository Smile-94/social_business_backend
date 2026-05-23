from django.urls import include, path, re_path

from apps.common.views.common_views import custom_404_handler

# All routes here are scoped to the active tenant schema
urlpatterns = []

# Catch-all 404 for unmatched /api/* tenant routes
urlpatterns += [
    re_path(r"^api/.*$", custom_404_handler),
]

handler404 = "apps.common.views.common_views.custom_404_handler"
