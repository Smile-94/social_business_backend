from pydantic import Field, SecretStr

from config.django._base_config import DjangoConfig
from config.environment import EnvironmentChoices, env_config


class JWTConfig(DjangoConfig):
    ACCESS_TOKEN_LIFETIME: int = Field(default=3600, ge=1)
    REFRESH_TOKEN_LIFETIME: int = Field(default=1_209_600, ge=1)

    ROTATE_REFRESH_TOKENS: bool = Field(default=True)
    BLACKLIST_AFTER_ROTATION: bool = Field(default=True)
    AUTH_HEADER_TYPES: tuple[str, ...] = Field(default=("Bearer",))

    def as_django_settings(self) -> dict:
        return {
            "ACCESS_TOKEN_LIFETIME": self.ACCESS_TOKEN_LIFETIME,
            "REFRESH_TOKEN_LIFETIME": self.REFRESH_TOKEN_LIFETIME,
            "ROTATE_REFRESH_TOKENS": self.ROTATE_REFRESH_TOKENS,
            "BLACKLIST_AFTER_ROTATION": self.BLACKLIST_AFTER_ROTATION,
            "AUTH_HEADER_TYPES": self.AUTH_HEADER_TYPES,
        }


jwt_config = JWTConfig()
