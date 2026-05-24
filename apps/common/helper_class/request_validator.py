import logging
from typing import Literal

from _library.functions.parse_field_list import get_supported_field_list_string

from _library.functions.formatters import response_formatter
from apps.common.error_codes import BAD_REQUEST_DEVELOPER_ERROR, BAD_REQUEST_USER_ERROR
from apps.common.functions.payload_generator import get_payload_data
from apps.common.functions.validators import (
    validate_field_list,
    validate_ordering_fields,
    validate_query_params,
    validate_request_fields,
)

logger = logging.getLogger(__name__)

QueryType = Literal["list", "retrieve"]


class RequestValidator:
    """
    Reusable request validation helper for DRF API views.

    All methods return:
        - A formatted error Response if validation fails.
        - None if validation passes (caller proceeds normally).

    Usage:
        error = RequestValidator.validate_serializer(serializer, caller=self)
        if error:
            return error
    """

    # ------------------------------------------------------------------ #
    # Object / Queryset                                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def validate_object_found(queryset, pk, resource_name: str = "Resource", caller=None):
        """
        Returns an error response if the queryset is empty (object not found).

        Args:
            queryset:      Evaluated queryset or falsy value.
            pk:            The lookup key used — included in logs and response.
            resource_name: Human-readable name for the resource (e.g. "Employee").
            caller:        The calling view instance — used for structured logging.
        """
        if not queryset:
            logger.info(
                "Object not found.",
                extra={
                    "caller": _caller_name(caller),
                    "resource": resource_name,
                    "pk": pk,
                },
            )
            return response_formatter(
                BAD_REQUEST_USER_ERROR,
                {"message": f"{resource_name} not found.", "id": pk},
            )
        return None

    # ------------------------------------------------------------------ #
    # Payload / Fields                                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def validate_empty_data(request, serializer_class, caller=None):
        """Returns an error response if the request body is empty."""
        if not request.data:
            logger.warning("Empty request body received.", extra={"caller": _caller_name(caller)})
            return response_formatter(
                BAD_REQUEST_DEVELOPER_ERROR,
                {
                    "message": "No data provided.",
                    "errors": "Request body is empty.",
                    "payload": get_payload_data(serializer_class),
                },
            )
        return None

    @staticmethod
    def validate_invalid_fields(model_class, request_data, serializer_class, caller=None):
        """
        Returns an error response if the request contains fields not
        recognised by the model or serializer.
        """
        invalid_fields = validate_request_fields(
            model_class=model_class, request_data=request_data, serializer_class=serializer_class
        )
        if invalid_fields:
            logger.warning(
                "Unrecognised fields in request payload.",
                extra={"caller": _caller_name(caller), "invalid_fields": invalid_fields},
            )
            return response_formatter(
                BAD_REQUEST_DEVELOPER_ERROR,
                {"message": "Invalid fields provided.", "errors": invalid_fields, "payload": get_payload_data(serializer_class)},
            )
        return None

    @staticmethod
    def validate_serializer(serializer, caller=None):
        """Returns an error response if the serializer fails validation."""
        if not serializer.is_valid():
            logger.warning("Serializer validation failed.", extra={"caller": _caller_name(caller), "errors": serializer.errors})
            return response_formatter(BAD_REQUEST_USER_ERROR, {"message": "Data validation error.", "errors": serializer.errors})
        return None

    @staticmethod
    def validate_query_params(request, query_filter, query_type: QueryType, caller=None):
        """
        Returns an error response if the request contains unsupported
        query parameters for the given query_type ('list' or 'retrieve').

        Raises:
            ValueError: If query_type is not 'list' or 'retrieve'.
        """
        if query_type not in ("list", "retrieve"):
            raise ValueError(f"validate_query_params: unsupported query_type '{query_type}'. Expected 'list' or 'retrieve'.")

        valid_params, invalid_params = validate_query_params(request, query_filter, query_type=query_type)

        if invalid_params:
            logger.warning(
                "Unsupported query parameters in request.",
                extra={"caller": _caller_name(caller), "query_type": query_type, "invalid_params": invalid_params},
            )
            return response_formatter(
                BAD_REQUEST_DEVELOPER_ERROR,
                {"message": "Invalid query parameters.", "invalid_params": invalid_params, "supported_params": valid_params},
            )
        return None

    @staticmethod
    def validate_query_field_list(field_list, serializer_class, model_class, caller=None):
        """
        Returns an error response if field_list contains fields not
        supported by the serializer or model.
        """
        invalid_fields = validate_field_list(field_list, serializer_class=serializer_class, model_class=model_class)
        if invalid_fields:
            logger.warning(
                "Unsupported fields in field_list parameter.",
                extra={"caller": _caller_name(caller), "invalid_fields": invalid_fields},
            )
            return response_formatter(
                BAD_REQUEST_DEVELOPER_ERROR,
                {
                    "message": "Invalid fields in 'field_list' parameter.",
                    "invalid_fields": invalid_fields,
                    "supported_fields": get_supported_field_list_string(serializer_class),
                },
            )
        return None

    @staticmethod
    def validate_ordering_fields(request, filter_map, caller=None):
        """
        Returns an error response if the ordering parameter contains
        unsupported fields. Returns None if ordering is absent or valid.
        """
        requested_fields = request.query_params.get("ordering")
        if not requested_fields:
            return None

        result = validate_ordering_fields(requested_fields, mapping=filter_map)
        invalid_fields = result["invalid_fields"]
        valid_fields = result["validated_fields"]

        if invalid_fields:
            logger.warning(
                "Unsupported ordering fields in request.",
                extra={"caller": _caller_name(caller), "invalid_fields": invalid_fields},
            )
            return response_formatter(
                BAD_REQUEST_DEVELOPER_ERROR,
                {"message": "Invalid ordering fields.", "invalid_fields": invalid_fields, "supported_fields": valid_fields},
            )
        return None


def _caller_name(caller) -> str:
    """Extracts a clean class name from the calling view for structured logs."""
    if caller is None:
        return "unknown"
    return type(caller).__name__ if not isinstance(caller, str) else caller
