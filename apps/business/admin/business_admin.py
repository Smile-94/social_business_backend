from django.contrib import admin
from rangefilter.filters import DateTimeRangeFilterBuilder

from apps.business.models.business_models import BusinessPermission, BusinessRole, BusinessRolePermission, BusinessUser


# <<------------------------------------Business User Admin---------------------------------------->>
@admin.register(BusinessUser)
class BusinessUserAdmin(admin.ModelAdmin):
    list_display = ("id", "user_id", "role", "invited_by", "created_at", "updated_at")
    list_filter = (
        "is_active",
        ("created_at", DateTimeRangeFilterBuilder()),
        ("updated_at", DateTimeRangeFilterBuilder()),
    )
    search_fields = ("user__username", "user__email")
    ordering = ("-id",)
    list_per_page = 20


# <<------------------------------------RBAC Permission Admin---------------------------------------->>
@admin.register(BusinessPermission)
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


# <<------------------------------------Role Admin---------------------------------------->>
@admin.register(BusinessRole)
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
@admin.register(BusinessRolePermission)
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
