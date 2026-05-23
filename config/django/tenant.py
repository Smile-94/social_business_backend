from pydantic import Field, SecretStr

from config.django._base_config import DjangoConfig


class TenantConfig(DjangoConfig):
    TENANT_MODEL: str = Field(
        default="tenant.Client",
        description="Custom tenant model. Must match the app label exactly.",
    )

    TENANT_DOMAIN_MODEL: str = Field(
        default="tenant.Domain",
        description="Custom domain model. Must match the app label exactly.",
    )

    DATABASE_ROUTERS: tuple[str] = ("django_tenants.routers.TenantSyncRouter",)

    def as_django_settings(self) -> dict:
        return {
            "TENANT_MODEL": self.TENANT_MODEL,
            "TENANT_DOMAIN_MODEL": self.TENANT_DOMAIN_MODEL,
            "DATABASE_ROUTERS": self.DATABASE_ROUTERS,
        }


tenant_config = TenantConfig()
