from datetime import timedelta

from pydantic import Field, SecretStr

from config.django._base_config import DjangoConfig
from config.django.security import security_config
from config.environment import EnvironmentChoices, env_config


class JWTConfig(DjangoConfig):
    # ── Lifetimes (stored as seconds, converted to timedelta on export) ───────
    ACCESS_TOKEN_LIFETIME: int = Field(default=3_600, ge=1)  # 1 hour
    REFRESH_TOKEN_LIFETIME: int = Field(default=1_209_600, ge=1)  # 14 days

    # ── Rotation & blacklist ──────────────────────────────────────────────────
    ROTATE_REFRESH_TOKENS: bool = Field(default=True)
    BLACKLIST_AFTER_ROTATION: bool = Field(default=True)

    # ── Signing ───────────────────────────────────────────────────────────────
    ALGORITHM: str = Field(default="HS256")
    SIGNING_KEY: SecretStr = Field(default=security_config.SECRET_KEY)

    # ── Transport ─────────────────────────────────────────────────────────────
    AUTH_HEADER_TYPES: tuple[str, ...] = Field(default=("Bearer",))
    AUTH_HEADER_NAME: str = Field(default="HTTP_AUTHORIZATION")

    # ── Claims ────────────────────────────────────────────────────────────────
    USER_ID_FIELD: str = Field(default="id")
    USER_ID_CLAIM: str = Field(default="user_id")
    TOKEN_TYPE_CLAIM: str = Field(default="token_type")

    # ── Custom serializer (adds username, email, user_type, is_staff) ─────────
    TOKEN_OBTAIN_SERIALIZER: str = Field(
        default="apps.authentication.serializers.authentication_serializers.CustomTokenObtainPairSerializer"
    )

    def as_django_settings(self) -> dict:
        return {
            # timedelta conversion happens here — Simple JWT will break without it
            "ACCESS_TOKEN_LIFETIME": timedelta(seconds=self.ACCESS_TOKEN_LIFETIME),
            "REFRESH_TOKEN_LIFETIME": timedelta(seconds=self.REFRESH_TOKEN_LIFETIME),
            "ROTATE_REFRESH_TOKENS": self.ROTATE_REFRESH_TOKENS,
            "BLACKLIST_AFTER_ROTATION": self.BLACKLIST_AFTER_ROTATION,
            "ALGORITHM": self.ALGORITHM,
            "SIGNING_KEY": self.SIGNING_KEY.get_secret_value(),
            "AUTH_HEADER_TYPES": self.AUTH_HEADER_TYPES,
            "AUTH_HEADER_NAME": self.AUTH_HEADER_NAME,
            "USER_ID_FIELD": self.USER_ID_FIELD,
            "USER_ID_CLAIM": self.USER_ID_CLAIM,
            "TOKEN_TYPE_CLAIM": self.TOKEN_TYPE_CLAIM,
            "TOKEN_OBTAIN_SERIALIZER": self.TOKEN_OBTAIN_SERIALIZER,
        }


jwt_config = JWTConfig()
