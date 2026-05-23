from django.contrib import admin
from rangefilter.filters import DateTimeRangeFilterBuilder

from apps.tenant.models.tenant_models import Client, Domain


# <<------------------------------------Tenant Admin---------------------------------------->>
@admin.register(Client)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "created_at", "updated_at")
    list_filter = (
        "is_active",
        ("created_at", DateTimeRangeFilterBuilder()),
        ("updated_at", DateTimeRangeFilterBuilder()),
    )
    search_fields = ("name", "slug", "domain")
    ordering = ("-id",)
    list_per_page = 20


# <<------------------------------------Tenant Domain Admin---------------------------------------->>
@admin.register(Domain)
class TenantDomainAdmin(admin.ModelAdmin):
    list_display = ("id", "domain", "tenant", "is_primary", "created_at", "updated_at")
    list_filter = (
        "is_active",
        ("created_at", DateTimeRangeFilterBuilder()),
        ("updated_at", DateTimeRangeFilterBuilder()),
    )
    search_fields = ("domain", "tenant")
    ordering = ("-id",)
    list_per_page = 20
