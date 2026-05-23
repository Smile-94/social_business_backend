from typing import Any

from pydantic import Field, computed_field

from config.django._base_config import DjangoConfig
from config.environment import EnvironmentChoices, env_config


class RestFrameworkConfig(DjangoConfig):
    """
    Django REST Framework configuration loaded via Pydantic.
    """

    DEFAULT_AUTHENTICATION_CLASSES: list[str] = Field(
        default=[
            "rest_framework_simplejwt.authentication.JWTAuthentication",
            "rest_framework.authentication.SessionAuthentication",
            "rest_framework.authentication.BasicAuthentication",
            "rest_framework.authentication.TokenAuthentication",
        ]
    )

    DEFAULT_THROTTLE_CLASSES: list[str] = Field(
        default=[
            "rest_framework.throttling.AnonRateThrottle",
            "rest_framework.throttling.UserRateThrottle",
            "rest_framework.throttling.ScopedRateThrottle",
        ]
    )

    DEFAULT_THROTTLE_RATES: dict[str, str] = Field(
        default={
            "auth": "5/min",
            "anon": "1000/hour",
            "user": "1000/hour",
            "scoped": "1000/hour",
        }
    )

    DEFAULT_PARSER_CLASSES: list[str] = Field(
        default=[
            "rest_framework.parsers.JSONParser",
            "rest_framework.parsers.FormParser",
            "rest_framework.parsers.MultiPartParser",
        ]
    )

    EXCEPTION_HANDLER: str = Field(default="apps.common.exception_handler.exception_handler")
    DEFAULT_PAGINATION_CLASS: str = Field(default="rest_framework.pagination.LimitOffsetPagination")
    PAGE_SIZE: int = Field(default=10, ge=1)
    DEFAULT_TIMEOUT: int = Field(default=3600, ge=1)
    DEFAULT_SCHEMA_CLASS: str = Field(default="drf_spectacular.openapi.AutoSchema")

    @computed_field
    def REST_FRAMEWORK(self) -> dict[str, Any]:
        """
        Assembles the final REST_FRAMEWORK dictionary.
        Dynamically adjusts permissions and renderers based on the environment
        without mutating class state.

        Note: DeviceTokenAuthentication was removed from permissions as it belongs
        strictly in DEFAULT_AUTHENTICATION_CLASSES.
        """
        is_production = env_config.ENVIRONMENT == EnvironmentChoices.PRODUCTION

        permissions = ["rest_framework.permissions.IsAuthenticated"] if is_production else ["rest_framework.permissions.AllowAny"]

        renderers = ["rest_framework.renderers.JSONRenderer"]
        if not is_production:
            renderers.append("rest_framework.renderers.BrowsableAPIRenderer")

        return {
            "DEFAULT_PERMISSION_CLASSES": permissions,
            "DEFAULT_AUTHENTICATION_CLASSES": self.DEFAULT_AUTHENTICATION_CLASSES,
            "DEFAULT_THROTTLE_CLASSES": self.DEFAULT_THROTTLE_CLASSES,
            "DEFAULT_THROTTLE_RATES": self.DEFAULT_THROTTLE_RATES,
            "DEFAULT_PARSER_CLASSES": self.DEFAULT_PARSER_CLASSES,
            "DEFAULT_RENDERER_CLASSES": renderers,
            "EXCEPTION_HANDLER": self.EXCEPTION_HANDLER,
            "DEFAULT_PAGINATION_CLASS": self.DEFAULT_PAGINATION_CLASS,
            "PAGE_SIZE": self.PAGE_SIZE,
            "DEFAULT_TIMEOUT": self.DEFAULT_TIMEOUT,
            "DEFAULT_SCHEMA_CLASS": self.DEFAULT_SCHEMA_CLASS,
        }

    def as_django_settings(self) -> dict:
        return {
            "REST_FRAMEWORK": self.REST_FRAMEWORK,
        }


drf_config = RestFrameworkConfig()
