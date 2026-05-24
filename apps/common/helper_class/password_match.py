# apps/common/validators/password_match.py

from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError as DRFValidationError


class PasswordMatchValidator:
    """
    Validates that password and confirm_password fields match.

    - Raises DRF or Django ValidationError based on context.
    - Removes confirm_password from attrs after validation
      so it never reaches the service or model layer.
    - Handles missing fields explicitly with clear error messages.

    Usage in DRF serializer (default):
        def validate(self, attrs):
            return PasswordMatchValidator()(attrs)

    Usage with custom field names:
        def validate(self, attrs):
            return PasswordMatchValidator(
                password_field="new_password",
                confirm_password_field="new_password_confirm",
            )(attrs)

    Usage in service/non-DRF context:
        PasswordMatchValidator(use_drf=False)(attrs)
    """

    def __init__(
        self, password_field: str = "password", confirm_field: str = "confirm_password", message: str = None, use_drf: bool = True
    ):
        self.password_field = password_field
        self.confirm_field = confirm_field
        self.message = message or _("Passwords do not match.")
        self.use_drf = use_drf

    def __call__(self, attrs: dict) -> dict:
        """
        Validates password match.

        Args:
            attrs: The full validated attrs dict from serializer.validate()

        Returns:
            attrs with confirm_password removed — never reaches service/model.

        Raises:
            DRFValidationError:    If use_drf=True  (default, serializer context)
            DjangoValidationError: If use_drf=False (forms, service context)
        """
        self._validate_fields_present(attrs)
        self._validate_passwords_match(attrs)

        attrs.pop(self.confirm_field, None)
        return attrs

    def _validate_fields_present(self, attrs: dict) -> None:
        """
        Raises a clear error if either field is absent entirely.
        Prevents silent None == None pass-through.
        """
        missing = []

        if self.password_field not in attrs:
            missing.append(self.password_field)
        if self.confirm_field not in attrs:
            missing.append(self.confirm_field)

        if missing:
            errors = {field: _("This field is required.") for field in missing}
            self._raise(errors)

    def _validate_passwords_match(self, attrs: dict) -> None:
        """Raises if password and confirm_password differ."""
        if attrs[self.password_field] != attrs[self.confirm_field]:
            self._raise({self.confirm_field: self.message})

    def _raise(self, errors: dict) -> None:
        """Raises the correct exception type based on use_drf flag."""
        if self.use_drf:
            raise DRFValidationError(errors)
        raise DjangoValidationError(errors)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(password_field={self.password_field!r}, confirm_field={self.confirm_field!r})"
