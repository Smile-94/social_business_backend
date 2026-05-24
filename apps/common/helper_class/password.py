# apps/common/validators/password.py

import logging
import re

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError as DRFValidationError

logger = logging.getLogger(__name__)


_UPPERCASE_RE = re.compile(r"[A-Z]")
_LOWERCASE_RE = re.compile(r"[a-z]")
_DIGIT_RE = re.compile(r"\d")
_SPECIAL_CHAR_RE = re.compile(r"[^A-Za-z0-9]")


def _get_password_errors(value: str, min_length: int) -> list[str]:
    """
    Pure validation logic — no framework dependency.
    Returns a list of error strings. Empty list means valid.

    Used by:
        - StrongPasswordValidator (Django AUTH_PASSWORD_VALIDATORS)
        - DRFPasswordValidator (DRF serializer fields)
        - Service layer (validate raw passwords directly)
    """
    errors = []

    if len(value) < min_length:
        errors.append(_(f"Password must be at least {min_length} characters long."))
    if not _UPPERCASE_RE.search(value):
        errors.append(_("Must contain at least one uppercase letter."))

    if not _LOWERCASE_RE.search(value):
        errors.append(_("Must contain at least one lowercase letter."))

    if not _DIGIT_RE.search(value):
        errors.append(_("Must contain at least one number."))

    if not _SPECIAL_CHAR_RE.search(value):
        errors.append(_("Must contain at least one special character."))

    return errors


class StrongPasswordValidator:
    """
    Django-native password validator.

    Register in settings.py under AUTH_PASSWORD_VALIDATORS so it
    runs automatically on set_password() and validate_password().

    Settings:
        AUTH_PASSWORD_VALIDATORS = [
            {
                "NAME": "apps.common.validators.password.StrongPasswordValidator",
                "OPTIONS": {"min_length": 10},   # optional override
            },
        ]
    """

    def __init__(self, min_length: int = 8):
        self.min_length = min_length

    def validate(self, password: str, user=None) -> None:
        """
        Called by Django's validate_password() and set_password().
        Raises django.core.exceptions.ValidationError on failure.
        """
        errors = _get_password_errors(password, self.min_length)
        if errors:
            raise DjangoValidationError(errors)

    def get_help_text(self) -> str:
        """
        Shown to users on registration/password-change pages
        BEFORE they type — so they know the rules upfront.
        """
        return _(
            f"Your password must be at least {self.min_length} characters long "
            f"and contain at least one uppercase letter, one lowercase letter, "
            f"one number, and one special character."
        )


class DRFPasswordValidator:
    """
    DRF-compatible password validator for use in serializer fields.

    Usage:
        from apps.common.validators.password import DRFPasswordValidator

        class CreateUserSerializer(serializers.Serializer):
            password = serializers.CharField(
                validators=[DRFPasswordValidator()]
            )
    """

    def __init__(self, min_length: int = 8):
        self.min_length = min_length

    def __call__(self, value: str) -> None:
        """
        Raises rest_framework.exceptions.ValidationError on failure.
        Returns None on success (DRF validators don't return values).
        """
        errors = _get_password_errors(value, self.min_length)
        if errors:
            raise DRFValidationError(errors)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(min_length={self.min_length})"
