# apps/common/exception_handler.py

import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import (
    AuthenticationFailed,
    MethodNotAllowed,
    NotAuthenticated,
    NotFound,
    PermissionDenied,
    Throttled,
    ValidationError as DRFValidationError,
)
from rest_framework.views import exception_handler as drf_exception_handler

from _library.functions.formatters import response_formatter
from apps.common.error_codes import (
    BAD_REQUEST_USER_ERROR,
    CONFLICT_ERROR,
    INTERNAL_SERVER_ERROR,
    METHOD_NOT_ALLOWED_ERROR,
    NOT_FOUND_ERROR,
    PERMISSION_DENIED_ERROR,
    THROTTLED_ERROR,
    UNAUTHORIZED_ERROR,
)
from apps.common.helper_class.exceptions import ConflictError, ServiceValidationError

logger = logging.getLogger(__name__)


def exception_handler(exc, context):
    """
    Global DRF exception handler.

    Resolution order:
        1. Custom domain exceptions  (ConflictError, ServiceValidationError)
        2. Django ValidationError    (from full_clean())
        3. DRF exceptions            (ValidationError, NotFound, etc.)
        4. Unhandled exceptions      (500)

    All responses follow the standard envelope:
        {
            "status":  <int>,
            "type":    "error",
            "message": <str>,
            "client":  "user" | "developer",
            "data":    {"errors": <dict|list>}
        }
    """

    view_name = _get_view_name(context)

    # ------------------------------------------------------------------ #
    # 1. Custom domain exceptions                                         #
    # ------------------------------------------------------------------ #

    if isinstance(exc, ServiceValidationError):
        logger.warning(
            "Service validation error.",
            extra={"view": view_name, "message": exc.message, "code": exc.code},
        )
        return response_formatter(
            BAD_REQUEST_USER_ERROR,
            {"message": exc.message, "errors": exc.message},
        )

    if isinstance(exc, ConflictError):
        logger.warning(
            "Conflict error.",
            extra={"view": view_name, "message": exc.message, "code": exc.code},
        )
        return response_formatter(
            CONFLICT_ERROR,
            {"message": exc.message, "errors": exc.message},
        )

    # ------------------------------------------------------------------ #
    # 2. Django ValidationError (from full_clean())                       #
    # ------------------------------------------------------------------ #

    if isinstance(exc, DjangoValidationError):
        errors = exc.message_dict if hasattr(exc, "message_dict") else {"non_field_errors": exc.messages}
        logger.warning(
            "Django validation error.",
            extra={"view": view_name, "errors": errors},
        )
        return response_formatter(
            BAD_REQUEST_USER_ERROR,
            {"message": "Data validation error.", "errors": errors},
        )

    # ------------------------------------------------------------------ #
    # 3. DRF exceptions                                                   #
    # ------------------------------------------------------------------ #

    response = drf_exception_handler(exc, context)

    if response is not None:
        return _format_drf_response(exc, response, view_name)

    # ------------------------------------------------------------------ #
    # 4. Unhandled exceptions → 500                                       #
    # ------------------------------------------------------------------ #

    logger.exception(
        "Unhandled exception.",
        extra={"view": view_name},
        # logger.exception() captures full traceback automatically
        # DO NOT put exc in the message — it double-logs
    )
    return response_formatter(INTERNAL_SERVER_ERROR)


# ------------------------------------------------------------------ #
# Private helpers                                                     #
# ------------------------------------------------------------------ #


def _format_drf_response(exc, response, view_name: str):
    """
    Maps DRF exception types to your standard response envelope.

    Each exception type gets:
        - The right error_code constant
        - A human-readable message
        - client: "user" or "developer" based on who caused it
    """

    if isinstance(exc, DRFValidationError):
        # Normalize DRF's error structure
        # DRF can return: {"field": ["msg"]} OR ["msg"] OR "msg"
        errors = _normalize_drf_errors(response.data)
        logger.warning(
            "DRF validation error.",
            extra={"view": view_name, "errors": errors},
        )
        return response_formatter(
            BAD_REQUEST_USER_ERROR,
            {"message": "Data validation error.", "errors": errors},
        )

    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        logger.info(
            "Authentication failed.",
            extra={"view": view_name, "detail": str(exc.detail)},
        )
        return response_formatter(
            UNAUTHORIZED_ERROR,
            {"message": "Authentication required.", "errors": str(exc.detail)},
        )

    if isinstance(exc, PermissionDenied):
        logger.info(
            "Permission denied.",
            extra={"view": view_name, "detail": str(exc.detail)},
        )
        return response_formatter(
            PERMISSION_DENIED_ERROR,
            {"message": "You do not have permission to perform this action.", "errors": str(exc.detail)},
        )

    if isinstance(exc, NotFound):
        logger.info(
            "Resource not found.",
            extra={"view": view_name, "detail": str(exc.detail)},
        )
        return response_formatter(
            NOT_FOUND_ERROR,
            {"message": "Resource not found.", "errors": str(exc.detail)},
        )

    if isinstance(exc, MethodNotAllowed):
        logger.warning(
            "Method not allowed.",
            extra={"view": view_name, "method": exc.args[0] if exc.args else "unknown"},
        )
        return response_formatter(
            METHOD_NOT_ALLOWED_ERROR,
            {"message": "Method not allowed.", "errors": str(exc.detail)},
        )

    if isinstance(exc, Throttled):
        logger.warning(
            "Request throttled.",
            extra={"view": view_name},
        )
        return response_formatter(
            THROTTLED_ERROR,
            {"message": "Too many requests. Please try again later.", "errors": str(exc.detail)},
        )

    # Fallback — known DRF exception but no specific handler
    logger.warning(
        "Unhandled DRF exception.",
        extra={"view": view_name, "exc_type": type(exc).__name__},
    )
    return response_formatter(
        INTERNAL_SERVER_ERROR,
        {"message": "An unexpected error occurred.", "errors": str(exc)},
    )


def _normalize_drf_errors(data) -> dict | list:
    """
    DRF validation errors come in inconsistent shapes.
    Normalize all of them to a consistent dict or list.

    Shapes DRF can return:
        {"field": ["error msg"]}           → field errors    → return as-is
        {"non_field_errors": ["msg"]}      → non-field       → return as-is
        ["error msg"]                      → list            → return as-is
        "error msg"                        → plain string    → wrap in list
    """
    if isinstance(data, dict):
        return data
    if isinstance(data, list):
        return data
    return [str(data)]


def _get_view_name(context: dict) -> str:
    """Safely extract view class name from DRF exception context."""
    view = context.get("view")
    if view is None:
        return "unknown"
    return type(view).__name__
