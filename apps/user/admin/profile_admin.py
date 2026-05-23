from django.contrib import admin
from rangefilter.filters import DateTimeRangeFilterBuilder

from apps.user.models.profile_model import UserAddress, UserProfile


# <<------------------------------------User Profile Admin---------------------------------------->>
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user__id",
        "user",
        "first_name",
        "last_name",
        "gender",
        "date_of_birth",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "gender",
        ("created_at", DateTimeRangeFilterBuilder()),
        ("updated_at", DateTimeRangeFilterBuilder()),
    )
    search_fields = ("user__username", "first_name", "last_name", "gender", "profile_photo", "date_of_birth")
    ordering = ("-id",)
    list_per_page = 20


# <<------------------------------------User Address Admin---------------------------------------->>
@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user__id",
        "user",
        "address_type",
        "city",
        "state",
        "country__id",
        "country",
        "zip_code",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "is_active",
        "address_type",
        ("created_at", DateTimeRangeFilterBuilder()),
        ("updated_at", DateTimeRangeFilterBuilder()),
    )
    search_fields = ("user__username", "address", "city", "state", "country", "zip_code")
    ordering = ("-id",)
    list_per_page = 20
