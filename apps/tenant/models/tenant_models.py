from django.db import models
from django_tenants.models import DomainMixin, TenantMixin

from apps.common.models.common_models import BaseModel, TimeStampedModel, UserStampModel


class Client(TenantMixin, BaseModel, TimeStampedModel, UserStampModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    # TenantMixin provides: schema_name, created_on
    auto_create_schema = True

    class Meta:
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"

    def __str__(self) -> str:
        return f"{self.name} ({self.schema_name})"

    def __repr__(self) -> str:
        return f"<Client: {self.name}, {self.pk}>"


class Domain(DomainMixin, BaseModel, TimeStampedModel, UserStampModel):
    """
    Maps hostnames → tenants.

    DomainMixin provides: domain, tenant (FK→Client), is_primary
    Examples:
      acme.yoursaas.com  →  Client(schema_name='acme')
      beta.yoursaas.com  →  Client(schema_name='beta')
    """

    class Meta:
        verbose_name = "Domain"
        verbose_name_plural = "Domains"

    def __str__(self) -> str:
        return self.domain

    def __repr__(self) -> str:
        return f"<Domain: {self.domain}, {self.pk}>"
