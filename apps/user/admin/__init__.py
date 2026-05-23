from apps.user.admin.activity_admin import UserActivityAdmin
from apps.user.admin.profile_admin import UserAddressAdmin, UserProfileAdmin
from apps.user.admin.rbac_admin import RBACPermissionAdmin
from apps.user.admin.role_admin import RoleAdmin, RolePermissionAdmin
from apps.user.admin.user_admin import UserAdmin

__all__ = [
    "RBACPermissionAdmin",
    "RoleAdmin",
    "RolePermissionAdmin",
    "UserAdmin",
    "UserAddressAdmin",
    "UserProfileAdmin",
    "UserActivityAdmin",
]
