from django.db import models

from apps.common.models.common_models import BaseModel, Country, SoftDeleteModel, TimeStampedModel
from apps.user.models.choices import AddressTypeChoices, GenderChoices
from apps.user.models.user_model import User


# <<------------------------------------- User Profile Model ------------------------------------->>
class UserProfile(BaseModel, TimeStampedModel, SoftDeleteModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_profile")
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(
        max_length=20, choices=GenderChoices.choices, default=GenderChoices.UNMENTIONED, blank=True, null=True
    )
    profile_photo = models.ImageField(upload_to="user_documents/", null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    class Meta:
        app_label = "user"
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        db_table = "user_profile"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def __repr__(self):
        return f"<UserProfile: {self.user.username}, {self.pk} profile>"


class UserAddress(BaseModel, TimeStampedModel, SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_address")
    address = models.CharField(max_length=100, null=True, blank=True)
    address_type = models.CharField(max_length=20, choices=AddressTypeChoices.choices, default=AddressTypeChoices.HOME.value)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, related_name="user_address_country", null=True, blank=True)
    country_name = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        app_label = "user"
        verbose_name = "User Address"
        verbose_name_plural = "User Addresses"
        db_table = "user_address"

    def get_full_address(self):
        return f"{self.address}, {self.city}, {self.state}, {self.country}, {self.zip_code}"

    def __str__(self):
        return f"{self.user.username}'s Address"

    def __repr__(self):
        return f"<UserAddress: {self.user.username}, {self.pk} address>"
