from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from rangefilter.filters import DateTimeRangeFilterBuilder

from apps.user.models.activity_model import UserActivity


# <<------------------------------------User Activity Admin---------------------------------------->>
@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by_id", "activity_type", "action_model", "action_id", "created_at", "updated_at")
    list_filter = (
        "activity_type",
        ("created_at", DateTimeRangeFilterBuilder()),
        ("updated_at", DateTimeRangeFilterBuilder()),
    )
    search_fields = ("user__username", "user__email")
    ordering = ("-id",)
    list_per_page = 20
