from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models.common_models import SoftDeleteModel, TimeStampedModel
from apps.user.models.choices import UserTypeChoices
from apps.user.models.role_model import Role


# <<------------------------------------User Model Manager---------------------------------------->>
class UserManager(BaseUserManager):
    def create_superuser(self, username, email, password, **extra_fields):
        """
        Admins/Superusers should always have a username, email, and password.
        """
        if not username or not email or not password:
            raise ValueError(_("Superusers must have a username, email, and password."))

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(username=username, email=email, password=password, **extra_fields)

    def create_user(self, username=None, email=None, phone=None, password=None, **extra_fields):
        """
        Creates a regular user. Requires AT LEAST ONE identifier
        (username, email, or phone).
        """
        if not username and not email and not phone:
            raise ValueError(_("You must provide at least one identifier: username, email, or phone."))

        if email:
            email = self.normalize_email(email)

        user = self.model(username=username, email=email, phone=phone, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.full_clean()
        user.save(using=self._db)

        return user


# <<------------------------------------User Model---------------------------------------->>
class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel, SoftDeleteModel):
    username = models.CharField(max_length=100, unique=True, null=True, blank=True, validators=[UnicodeUsernameValidator()])
    email = models.EmailField(_("email_address"), unique=True, null=True, blank=True)
    phone = models.CharField(max_length=100, unique=True, null=True, blank=True)
    role = models.ForeignKey(Role, blank=True, null=True, on_delete=models.SET_NULL, related_name="user_role")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    user_type = models.CharField(max_length=20, choices=UserTypeChoices.choices, default=UserTypeChoices.BUSINESS.value)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()

    class Meta:
        app_label = "user"
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def get_user_rbac_permissions(self):
        return self.role.permissions.all().prefetch_related("permissions")

    def get_short_name(self):
        return self.username

    def __str__(self):
        return f"{self.username}"

    def __repr__(self):
        return f"<User: {self.username}, {self.pk}>"
