from pydantic import Field, computed_field

from config.django._base_config import DjangoConfig
from config.environment import EnvironmentChoices, env_config


class MiddlewareConfig(DjangoConfig):
    """
    Django middleware configuration assembled via Pydantic.
    """

    CORE_MIDDLEWARE: list[str] = Field(
        default=[
            "django_tenants.middleware.main.TenantMainMiddleware",
            "django.middleware.security.SecurityMiddleware",
            "corsheaders.middleware.CorsMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
        ]
    )

    THIRD_PARTY_MIDDLEWARE: list[str] = Field(
        default=[
            "whitenoise.middleware.WhiteNoiseMiddleware",
            "csp.middleware.CSPMiddleware",
        ]
    )

    CUSTOM_MIDDLEWARE: list[str] = Field(default=["apps.common.middleware.custom_middleware.RequestLoggingMiddleware"])

    @computed_field
    def MIDDLEWARE(self) -> list[str]:
        """Combine core, third-party, and custom middleware into the final list."""
        middleware = self.CORE_MIDDLEWARE + self.THIRD_PARTY_MIDDLEWARE + self.CUSTOM_MIDDLEWARE

        # Inject debug toolbar only in safe environments
        if env_config.ENVIRONMENT in (EnvironmentChoices.LOCAL, EnvironmentChoices.DEVELOPMENT):
            # The Debug Toolbar docs recommend placing its middleware as early as possible
            middleware.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")

        return middleware

    def as_django_settings(self) -> dict:
        return {
            "MIDDLEWARE": self.MIDDLEWARE,
        }


# Singleton middleware configuration instance
middleware_config = MiddlewareConfig()
