from dataclasses import dataclass
import logging
from typing import Any

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from apps.common.helper_class.exceptions import ConflictError, ServiceValidationError
from apps.user.models.choices import UserTypeChoices

logger = logging.getLogger(__name__)
User = get_user_model()


# ------------------------------------------------------------------ #
# Result object — never return raw model instances from a service     #
# ------------------------------------------------------------------ #


@dataclass(frozen=True)
class CreateUserResult:
    user: User
    created: bool


# ------------------------------------------------------------------ #
# Service                                                             #
# ------------------------------------------------------------------ #


class BusinessUserService:
    """
    Handles all business logic for Business-type user accounts.

    Responsibilities:
        - User creation with strict field allowlist
        - Audit logging (who triggered the action)
        - Structured logging for observability
        - Explicit error mapping (no naked exceptions)

    Usage:
        service = BusinessUserService()
        result  = service.create_user(validated_data, action_user=request.user)
    """

    ALLOWED_CREATE_FIELDS: frozenset[str] = frozenset({"username", "email", "password", "phone"})

    def __init__(self, user_model=None):
        self._model = user_model or User

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def create_user(self, validated_data: dict[str, Any], action_user: Any = None) -> CreateUserResult:
        """
        Creates a new Business-type user account.

        Args:
            validated_data: Cleaned data from a validated serializer.
                            Only fields in ALLOWED_CREATE_FIELDS are used.
            action_user:    The user (or system) triggering this action.
                            Used for audit logging.

        Returns:
            CreateUserResult with the created User and created=True.

        Raises:
            ServiceValidationError: If required fields are missing.
            ConflictError:          If a user with the same unique
                                    field (email/username) already exists.
        """
        self._validate_required_fields(validated_data)

        safe_data = self._extract_safe_fields(validated_data)

        logger.info(
            "Creating business user.",
            extra={
                "username": safe_data.get("username"),
                "email": safe_data.get("email"),
                "action_by": _actor_label(action_user),
            },
        )

        try:
            user = self._persist_user(safe_data)
        except IntegrityError as exc:
            self._handle_integrity_error(exc, safe_data, action_user)

        logger.info(
            "Business user created successfully.",
            extra={"user_id": user.pk, "username": user.username, "action_by": _actor_label(action_user)},
        )

        return CreateUserResult(user=user, created=True)

    # ------------------------------------------------------------------ #
    # Private — persistence                                               #
    # ------------------------------------------------------------------ #

    @transaction.atomic
    def _persist_user(self, safe_data: dict[str, Any]) -> User:
        """
        Atomic persistence layer.
        Isolated here so the public method stays readable and
        the transaction boundary is explicit and intentional.
        """
        password = safe_data.pop("password")

        user = self._model(
            **safe_data,
            user_type=UserTypeChoices.BUSINESS.value,
        )
        user.set_password(password)  # ← never pass raw password to create()
        user.full_clean()  # ← triggers model-level validation
        user.save()

        return user

    # ------------------------------------------------------------------ #
    # Private — validation                                                #
    # ------------------------------------------------------------------ #

    def _validate_required_fields(self, data: dict[str, Any]) -> None:
        """Raises ServiceValidationError if critical fields are absent."""
        required = {"username", "email", "password", "phone"}
        missing = required - data.keys()
        if missing:
            raise ServiceValidationError(f"Missing required fields: {', '.join(sorted(missing))}")

    def _extract_safe_fields(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Returns only allowlisted fields.
        Logs any fields that were stripped (useful for catching
        serializer bugs or probing attempts).
        """
        safe = {k: v for k, v in data.items() if k in self.ALLOWED_CREATE_FIELDS}
        stripped = data.keys() - safe.keys()

        if stripped:
            logger.warning("Stripped unexpected fields from user creation payload.", extra={"stripped_fields": sorted(stripped)})
        return safe

    # ------------------------------------------------------------------ #
    # Private — error handling                                            #
    # ------------------------------------------------------------------ #

    def _handle_integrity_error(self, exc: IntegrityError, safe_data: dict[str, Any], action_user: Any) -> None:
        """
        Maps DB IntegrityError to a domain exception.
        Never lets a raw DB error bubble up to the view layer.
        """
        error_str = str(exc).lower()

        logger.warning(
            "User creation failed due to integrity error.",
            extra={
                "username": safe_data.get("username"),
                "email": safe_data.get("email"),
                "action_by": _actor_label(action_user),
                "db_error": str(exc),
            },
        )

        if "username" in error_str:
            raise ConflictError("A user with this username already exists.") from exc
        if "email" in error_str:
            raise ConflictError("A user with this email already exists.") from exc

        raise ConflictError("User could not be created due to a conflict.") from exc


def _actor_label(action_user: Any) -> str:
    """Returns a clean string label for the acting user (for logs)."""
    if action_user is None:
        return "system"
    if hasattr(action_user, "pk"):
        return f"user:{action_user.pk}"
    return str(action_user)
