from django.db import models

from apps.common.models.common_models import BaseModel, TimeStampedModel, UserStampModel
from apps.user.models.rbac_permission_model import RBACPermission


# <<------------------------------------Role Model Manager---------------------------------------->>
class RoleManager(models.Manager):
    def get_all_role(self):
        return self.all()

    def get_all_active_role(self):
        return self.filter(is_active=True)


# <<------------------------------------Role Model---------------------------------------->>
class Role(BaseModel, TimeStampedModel, UserStampModel):
    name = models.CharField(max_length=100, null=False, blank=False)

    objects = RoleManager()

    class Meta:
        app_label = "user"
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        db_table = "role"

    @property
    def extracted_permissions(self):
        """
        Extracts the RBACPermission objects from the intermediate table.
        Uses the prefetch_related data from the Selector.
        """
        return [rp.permission for rp in self.rolepermission_set.all()]

    def __str__(self):
        return self.name


# <<------------------------------------Role Permission Model---------------------------------------->>
class RolePermission(BaseModel, TimeStampedModel, UserStampModel):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=False, blank=False)
    permission = models.ForeignKey(
        RBACPermission, related_name="role_permissions", on_delete=models.CASCADE, null=False, blank=False
    )

    class Meta:
        verbose_name = "Role Permission"
        verbose_name_plural = "Role Permissions"
        db_table = "role_permission"
        unique_together = ("role", "permission")

    def __str__(self):
        return f"{self.role.name} >> {self.permission.name}"

    def __repr__(self):
        return f"<-- Role Permission {self.role.name} >> {self.permission.name} -->"
