from django.db import models

from apps.common.models.common_models import BaseModel, TimeStampedModel, UserStampModel


# <<------------------------------------RBAC Permission Model Manager---------------------------------------->>
class RBACPermissionManager(models.Manager):
    def get_all_permissions(self):
        return self.all()

    def get_all_active_permissions(self):
        return self.filter(is_active=True)


# <<------------------------------------RBAC Permission Model---------------------------------------->>
class RBACPermission(BaseModel, TimeStampedModel, UserStampModel):
    name = models.CharField(max_length=100, null=False, blank=False)
    code = models.CharField(max_length=100, null=False, blank=False, unique=True)
    for_permission = models.CharField(max_length=100, null=True, blank=True)

    objects = RBACPermissionManager()

    class Meta:
        app_label = "user"
        verbose_name = "RBAC Permission"
        verbose_name_plural = "RBAC Permissions"
        db_table = "rbac_permission"

    def __str__(self):
        return self.name
