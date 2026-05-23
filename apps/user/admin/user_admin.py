from django.contrib import admin
from rangefilter.filters import DateTimeRangeFilterBuilder

from apps.user.models.user_model import User


# <<------------------------------------User Admin---------------------------------------->>
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "is_active", "is_staff", "is_superuser", "created_at", "updated_at")
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        ("created_at", DateTimeRangeFilterBuilder()),
        ("updated_at", DateTimeRangeFilterBuilder()),
    )
    search_fields = ("username", "email", "phone")
    ordering = ("-id",)
    list_per_page = 20
