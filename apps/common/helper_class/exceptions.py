from rest_framework import status


class AppBaseException(Exception):
    """
    Base class for all application-level domain exceptions.

    All custom exceptions inherit from this so callers can catch
    either a specific exception or the entire app exception family.

        try:
            service.create_user(data)
        except AppBaseException as exc:       # catches ALL app errors
            ...
        except ConflictError as exc:          # catches only conflict
            ...
    """

    default_message: str = "An unexpected error occurred."
    default_code: str = "error"
    http_status: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str = None, code: str = None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, code={self.code!r})"


class ServiceValidationError(AppBaseException):
    """
    Raised when service-layer input validation fails BEFORE
    hitting the database — e.g. missing required fields,
    invalid combinations, or business rule violations.

    HTTP equivalent : 400 Bad Request
    Who handles it  : View layer → returns 400 response

    Example:
        if not data.get("email"):
            raise ServiceValidationError(
                message="Email is required.",
                code="missing_email",
            )
    """

    default_message = "Service validation failed."
    default_code = "validation_error"
    http_status = status.HTTP_400_BAD_REQUEST


class ConflictError(AppBaseException):
    """
    Raised when a DB uniqueness constraint is violated — e.g.
    duplicate email, username, or any unique_together combination.

    HTTP equivalent : 409 Conflict
    Who handles it  : View layer → returns 409 response

    Example:
        raise ConflictError(
            message="A user with this email already exists.",
            code="duplicate_email",
        )
    """

    default_message = "A conflict occurred with an existing record."
    default_code = "conflict"
    http_status = status.HTTP_409_CONFLICT
