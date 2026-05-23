from django.db import models

from apps.common.models.common_models import BaseModel, TimeStampedModel, UserStampModel


class BusinessPermission(BaseModel, TimeStampedModel, UserStampModel):
    name = models.CharField(max_length=100, null=False, blank=False)
    code = models.CharField(max_length=100, null=False, blank=False, unique=True)
    for_permission = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        app_label = "business"
        verbose_name = "Business Permission"
        verbose_name_plural = "Business Permissions"
        db_table = "business_permission"


class BusinessRole(BaseModel, TimeStampedModel, UserStampModel):
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)

    class Meta:
        app_label = "business"
        verbose_name = "Business Role"
        verbose_name_plural = "Business Roles"
        db_table = "business_role"


class BusinessRolePermission(BaseModel, TimeStampedModel, UserStampModel):
    role = models.ForeignKey(BusinessRole, on_delete=models.CASCADE, null=False, blank=False)
    permission = models.ForeignKey(
        BusinessPermission, related_name="business_role_permissions", on_delete=models.CASCADE, null=False, blank=False
    )

    class Meta:
        verbose_name = "Role Permission"
        verbose_name_plural = "Role Permissions"
        db_table = "business_role_permission"

    def __str__(self):
        return f"{self.role.name} >> {self.permission.name}"

    def __repr__(self):
        return f"<-- Role Permission {self.role.name} >> {self.permission.name} -->"


class BusinessUser(BaseModel, TimeStampedModel, UserStampModel):
    """
    Lives in each TENANT schema.
    Links a public-schema User (by ID only — no real FK across schemas)
    to a role within this tenant.
    """

    user_id = models.IntegerField(db_index=True)
    role = models.ForeignKey(BusinessRole, on_delete=models.CASCADE, null=False, blank=False)
    invited_by = models.IntegerField(null=True, blank=True)

    class Meta:
        app_label = "business"
        verbose_name = "Business User"
        verbose_name_plural = "Business Users"
        db_table = "business_user"

    def get_user(self):
        """Fetch the actual User object from the public schema."""
        from apps.user.models import User

        return User.objects.get(pk=self.user_id)

    def get_invited_by(self):
        """Fetch the actual User object from the public schema."""
        from apps.user.models import User

        if self.invited_by:
            return User.objects.get(pk=self.invited_by)
