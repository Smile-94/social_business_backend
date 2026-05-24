from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError


def convert_django_validation_error(exc: DjangoValidationError) -> DRFValidationError:
    """
    Converts django.core.exceptions.ValidationError
    to rest_framework.exceptions.ValidationError.

    full_clean() raises Django's version — DRF views only handle DRF's version.
    Without this, full_clean() errors become unhandled 500s.
    """
    return DRFValidationError(detail=exc.message_dict if hasattr(exc, "message_dict") else exc.messages)
