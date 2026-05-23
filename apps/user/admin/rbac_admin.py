from django.contrib import admin
from rangefilter.filters import DateTimeRangeFilterBuilder

from apps.user.models.rbac_permission_model import RBACPermission


# <<------------------------------------RBAC Permission Admin---------------------------------------->>
@admin.register(RBACPermission)
class RBACPermissionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "for_permission", "is_active", "created_at", "updated_at")
    list_filter = (
        "is_active",
        ("created_at", DateTimeRangeFilterBuilder()),
        ("updated_at", DateTimeRangeFilterBuilder()),
    )
    search_fields = ("name", "code", "for_permission")
    ordering = ("-id",)
    list_per_page = 20
