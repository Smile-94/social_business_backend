from django.urls import path

from apps.authentication.views.authentication_views import (
    BusinessLoginView,
    BusinessRegisterView,
    LogoutView,
    TokenRefreshViewExtended,
)

app_name = "auth"

urlpatterns = [
    # Registration
    path("register/", BusinessRegisterView.as_view(), name="register"),
    # Login — returns access + refresh tokens
    path("login/", BusinessLoginView.as_view(), name="login"),
    # Token management
    path("token/refresh/", TokenRefreshViewExtended.as_view(), name="token-refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
