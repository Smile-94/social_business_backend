import logging

from django.core.exceptions import NON_FIELD_ERRORS
from django.db import models
from django.db.models import Q
from rest_framework import serializers

logger = logging.getLogger(__name__)


class UniqueFieldsValidatorMixin:
    unique_fields: list[str] | None = None
    unique_together_fields: list[tuple] | None = None
    unique_validator_model = None

    def validate(self, attrs):
        attrs = super().validate(attrs)

        # Priority: explicit attr → Meta.model → skip
        model = self.unique_validator_model or self._get_model()
        if model is None:
            return attrs

        instance = getattr(self, "instance", None)
        self._validate_simple_unique_fields(attrs, model, instance)
        self._validate_composite_unique_fields(attrs, model, instance)
        return attrs

    def _get_model(self):
        try:
            return self.Meta.model
        except AttributeError:
            logger.warning(
                "%s: no Meta.model and unique_validator_model not set — skipping unique validation.",
                self.__class__.__name__,
            )
            return None

    def _validate_simple_unique_fields(self, attrs, model, instance):
        fields = self.unique_fields or self._detect_simple_unique_fields(model)
        if not fields:
            return

        # Build value map for fields present in incoming data only
        value_map = {field: attrs[field] for field in fields if field in attrs and attrs[field] is not None}
        if not value_map:
            return

        # Single query — fetch all potentially conflicting rows
        query = Q()
        for field, value in value_map.items():
            query |= Q(**{field: value})

        qs = model.objects.filter(query)

        # Exclude the current instance on updates
        if instance is not None:
            qs = qs.exclude(pk=instance.pk)

        # Fetch only the columns we care about
        conflicts = qs.values(*value_map.keys())

        if not conflicts:
            return

        # Map conflicting values back to field names — no extra queries
        errors = {}
        conflicting_values = {field: {row[field] for row in conflicts} for field in value_map}

        for field, value in value_map.items():
            if value in conflicting_values.get(field, set()):
                errors[field] = self._unique_error_message(field, value)

        if errors:
            raise serializers.ValidationError(errors)

    def _validate_composite_unique_fields(self, attrs, model, instance):
        constraint_groups = self.unique_together_fields or self._detect_composite_unique_fields(model)
        if not constraint_groups:
            return

        errors = {}

        for group in constraint_groups:
            # Only validate if ALL fields in the group are present
            if not all(f in attrs and attrs[f] is not None for f in group):
                continue

            lookup = {field: attrs[field] for field in group}
            qs = model.objects.filter(**lookup)

            if instance is not None:
                qs = qs.exclude(pk=instance.pk)

            if qs.exists():
                # Report error on the first field of the group, plus non-field
                key = group[0] if len(group) == 1 else NON_FIELD_ERRORS
                errors[key] = self._composite_unique_error_message(group, lookup)

        if errors:
            raise serializers.ValidationError(errors)

    # ------------------------------------------------------------------ #
    # Auto-detection                                                       #
    # ------------------------------------------------------------------ #

    def _detect_simple_unique_fields(self, model) -> list[str]:
        """Detect fields with unique=True, skipping PKs and non-editable fields."""
        fields = []
        for field in model._meta.get_fields():
            # Skip reverse relations and many-to-many
            if not hasattr(field, "column"):
                continue
            if isinstance(field, self._SKIP_FIELD_TYPES):
                continue
            if field.primary_key:
                continue
            if not getattr(field, "editable", True):
                continue
            if getattr(field, "unique", False):
                fields.append(field.name)
        return fields

    def _detect_composite_unique_fields(self, model) -> list[tuple]:
        """Detect unique_together + multi-field UniqueConstraints."""
        groups = []

        # Legacy unique_together
        for group in model._meta.unique_together:
            groups.append(tuple(group))

        # Modern UniqueConstraint
        for constraint in getattr(model._meta, "constraints", []):
            if not hasattr(constraint, "fields"):
                continue
            constraint_fields = tuple(constraint.fields)

            # Skip single-field constraints (handled as simple unique fields)
            if len(constraint_fields) < 2:
                continue

            # Skip partial constraints (condition=...) — let DB handle those
            if getattr(constraint, "condition", None) is not None:
                logger.debug(
                    "Skipping partial UniqueConstraint '%s' on %s — relies on DB-level enforcement.",
                    constraint.name,
                    model.__name__,
                )
                continue

            groups.append(constraint_fields)

        return groups

    @staticmethod
    def _unique_error_message(field: str, value) -> str:
        label = field.replace("_", " ").capitalize()
        return f"{label} with this value already exists."

    @staticmethod
    def _composite_unique_error_message(group: tuple, lookup: dict) -> str:
        label = " + ".join(f.replace("_", " ") for f in group)
        return f"The combination of {label} must be unique."
