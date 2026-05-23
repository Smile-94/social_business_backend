"""models module for common."""

from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


# <<------------------------------------Timestamped Model---------------------------------------->>
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# <<------------------------------------Soft Deleted Model---------------------------------------->>
class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


# <<------------------------------------User Stamp Model---------------------------------------->>
class UserStampModel(models.Model):
    """
    Stores user IDs as plain integers — safe for BOTH public and tenant schemas.
    Use get_created_by() / get_updated_by() to fetch the actual User object.
    """

    created_by_id = models.IntegerField(null=True, blank=True, db_index=True)
    updated_by_id = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True

    def get_created_by(self):
        from apps.user.models import User

        if self.created_by_id:
            return User.objects.get(pk=self.created_by_id)

    def get_updated_by(self):
        from apps.user.models import User

        if self.updated_by_id:
            return User.objects.get(pk=self.updated_by_id)


# <<------------------------------------Base Model---------------------------------------->>
class BaseModel(models.Model):
    """
    Base Model for all models
    """

    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, default="")

    class Meta:
        abstract = True


# * <<-------------------------------------*** COUNTRY ***----------------------------------------->>
class Country(BaseModel, TimeStampedModel, SoftDeleteModel, UserStampModel):
    country_name = models.CharField(max_length=50, unique=True)
    country_code = models.CharField(max_length=50)

    class Meta:
        app_label = "common"
        db_table = "country"
        verbose_name = "Country"
        verbose_name_plural = "Countries"

    def __str__(self):
        return f"{self.country_name}"

    def __repr__(self):
        return f"<Country: {self.country_name}({self.pk})>"
