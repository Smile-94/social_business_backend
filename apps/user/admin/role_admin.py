from django.contrib import admin
from rangefilter.filters import DateTimeRangeFilterBuilder

from apps.user.models.role_model import Role, RolePermission


# <<------------------------------------Role Admin---------------------------------------->>
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active", "created_at", "updated_at")
    list_filter = (
        "is_active",
        ("created_at", DateTimeRangeFilterBuilder()),
        ("updated_at", DateTimeRangeFilterBuilder()),
    )
    search_fields = ("name",)
    ordering = ("-id",)
    list_per_page = 20


# <<------------------------------------Role Permission Admin---------------------------------------->>
@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ("id", "role__id", "role", "permission__id", "permission", "is_active", "created_at", "updated_at")
    list_filter = (
        "is_active",
        ("created_at", DateTimeRangeFilterBuilder()),
        ("updated_at", DateTimeRangeFilterBuilder()),
    )
    search_fields = ("role__name", "permission__name")
    ordering = ("-id",)
    list_per_page = 20
