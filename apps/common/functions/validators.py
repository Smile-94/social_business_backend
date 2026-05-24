from collections.abc import Iterable
import logging
from typing import Any

from django.core.exceptions import FieldDoesNotExist
from django.db.models import Model
from rest_framework import serializers
from rest_framework.serializers import Serializer

logger = logging.getLogger(__name__)


def parse_field_string(field_input) -> dict:
    """
    Parses a nested field string into a dictionary.
    Example: "id, user(id, name)" -> {"id": "*", "user": "id, name"}
    """

    # 1. THE FIX: If it comes in as a list, join it into a string first!
    if isinstance(field_input, (list, tuple, set)):
        field_input = ",".join(str(f).strip() for f in field_input)

    if not isinstance(field_input, str):
        raise serializers.ValidationError({"field_list": "Must be '*' or list or string"})

    result = {}
    current_key = ""
    current_nested = ""
    depth = 0

    # 2. Character-by-character parser
    for char in field_input:
        if char == "(":
            depth += 1
            if depth > 1:
                current_nested += char
        elif char == ")":
            depth -= 1
            if depth > 0:
                current_nested += char
            elif depth == 0:
                result[current_key.strip()] = current_nested
                current_key = ""
                current_nested = ""
        elif char == "," and depth == 0:
            if current_key.strip():
                result[current_key.strip()] = "*"
                current_key = ""
        else:
            if depth == 0:
                current_key += char
            else:
                current_nested += char

    # Catch the last key if no trailing comma
    if current_key.strip():
        result[current_key.strip()] = "*"

    return result


def validate_request_fields(
    *,
    model_class: type[Model],
    request_data: dict[str, Any],
    serializer_class: type[Serializer] | None = None,
    extended_fields: Iterable[str] | None = None,
) -> Iterable[str]:
    """
    Validate incoming request fields against:
    - Django model fields
    - DRF serializer fields (if provided)
    - Optional extended/custom fields

    Returns:
        List[str]: List of invalid fields found in request_data.
                   Empty list if all fields are valid.

    Notes:
        This function does NOT raise ValidationError automatically.
        It logs any exceptions and returns invalid fields for further handling.
    """
    try:
        # 1. Collect model field names
        model_fields = {field.name for field in model_class._meta.fields}

        # 2. Collect serializer fields (if provided)
        serializer_fields = set()
        if serializer_class:
            serializer_fields = set(serializer_class().get_fields().keys())

        # 3. Include extended/custom fields
        extra_fields = set(extended_fields or [])

        # 4. Build final allowed fields set
        allowed_fields = model_fields | serializer_fields | extra_fields

        # 5. Detect invalid fields
        invalid_fields = [field for field in request_data.keys() if field not in allowed_fields]

        return invalid_fields

    except FieldDoesNotExist as e:
        # Log model field errors and return as invalid field
        logger.exception(f"Model field does not exist: {e}")
        return [str(e)]

    except Exception as e:
        # Log unexpected errors and return a descriptive invalid field
        logger.exception(f"Unexpected error validating request fields: {e}")
        return [f"Unexpected error: {str(e)}"]


def safe_split_fields(raw_string: str) -> list[str]:
    """
    Safely splits a string by commas, ignoring commas inside parentheses.
    Example: "id, client(id, name)" -> ["id", "client(id, name)"]
    """
    if not raw_string:
        return []

    tokens = []
    current = []
    depth = 0

    for char in raw_string:
        if char == "(":
            depth += 1
            current.append(char)
        elif char == ")":
            depth -= 1
            current.append(char)
        elif char == "," and depth == 0:
            tokens.append("".join(current).strip())
            current = []
        else:
            current.append(char)

    if current:
        tokens.append("".join(current).strip())

    return [t for t in tokens if t]


def _parse_string_to_dict(s: str) -> dict:
    """
    Safely parses a bracketed string into a nested dictionary.
    Example: 'id, designation(id, name)' -> {'id': '*', 'designation': {'id': '*', 'name': '*'}}
    """
    result = {}
    tokens = safe_split_fields(s)

    for token in tokens:
        if not token:
            continue
        if "(" in token and token.endswith(")"):
            parent_idx = token.index("(")
            parent = token[:parent_idx].strip()
            children_str = token[parent_idx + 1 : -1].strip()
            result[parent] = _parse_string_to_dict(children_str)
        else:
            result[token] = "*"

    return result


def validate_field_list(raw_fields, *, serializer_class=None, model_class=None) -> list[str]:
    """
    Validates requested fields against a DRF serializer and/or Django model.
    Accepts a raw query string (e.g., "id, client(name)") or a parsed dictionary.
    """
    if not raw_fields or raw_fields == "*":
        return []

    def _validate_recursive(parsed_fields, current_serializer=None, current_model=None, prefix=""):
        if not parsed_fields or parsed_fields == "*":
            return []

        # Normalization: Use our safe parser to handle strings with parentheses
        if isinstance(parsed_fields, str):
            parsed_fields = _parse_string_to_dict(parsed_fields)
        elif isinstance(parsed_fields, list):
            combined = {}
            for item in parsed_fields:
                if isinstance(item, str):
                    combined.update(_parse_string_to_dict(item))
            parsed_fields = combined
        elif not isinstance(parsed_fields, dict):
            parsed_fields = {}

        invalid = []
        allowed_fields = set()
        serializer_fields = {}

        # Gather allowed fields for the CURRENT level
        if current_serializer:
            inst = current_serializer() if isinstance(current_serializer, type) else current_serializer
            if hasattr(inst, "get_fields"):
                serializer_fields = inst.get_fields()
                allowed_fields |= set(serializer_fields.keys())

        if current_model:
            allowed_fields |= {field.name for field in current_model._meta.get_fields()}

        # Loop through properly parsed fields
        for field_name, nested_fields in parsed_fields.items():
            full_field_name = f"{prefix}{field_name}"

            if field_name == "*":
                continue

            # Check if the field itself is allowed
            if field_name not in allowed_fields:
                invalid.append(full_field_name)
                continue

            # If there are nested fields, recurse
            if nested_fields and nested_fields != "*":
                next_serializer = None
                next_model = None

                # Find the nested serializer
                if field_name in serializer_fields:
                    s_field = serializer_fields[field_name]
                    if hasattr(s_field, "child"):
                        next_serializer = s_field.child
                    elif hasattr(s_field, "get_fields"):
                        next_serializer = s_field

                # Find the related Django model
                if current_model:
                    try:
                        m_field = current_model._meta.get_field(field_name)
                        if m_field.is_relation and hasattr(m_field, "related_model"):
                            next_model = m_field.related_model
                    except FieldDoesNotExist:
                        pass

                # Recurse deeper into valid nested structure
                invalid.extend(
                    _validate_recursive(
                        nested_fields, current_serializer=next_serializer, current_model=next_model, prefix=f"{full_field_name}."
                    )
                )

        return invalid

    invalid_fields = _validate_recursive(raw_fields, current_serializer=serializer_class, current_model=model_class)
    return sorted(invalid_fields)


# def validate_field_list(field_list, *, serializer_class=None, model_class=None) -> list[str]:
#     if not field_list or field_list == "*":
#         return []

#     def _validate_recursive(parsed_fields, current_serializer=None, current_model=None, prefix=""):
#         # 1. Normalization: Convert strings/lists into a dictionary
#         if not parsed_fields or parsed_fields == "*":
#             return []

#         if isinstance(parsed_fields, str):
#             # Converts "id,genders" -> {"id": {}, "genders": {}}
#             parsed_fields = {k.strip(): {} for k in parsed_fields.split(",") if k.strip()}
#         elif isinstance(parsed_fields, list):
#             parsed_fields = {k: {} for k in parsed_fields}
#         elif not isinstance(parsed_fields, dict):
#             parsed_fields = {}

#         invalid = []
#         allowed_fields = set()
#         serializer_fields = {}

#         # 2. Gather allowed fields for the CURRENT level
#         if current_serializer:
#             inst = current_serializer() if isinstance(current_serializer, type) else current_serializer
#             if hasattr(inst, "get_fields"):
#                 serializer_fields = inst.get_fields()
#                 allowed_fields |= set(serializer_fields.keys())

#         if current_model:
#             allowed_fields |= {field.name for field in current_model._meta.get_fields()}

#         # 3. Loop through parsed fields
#         for field_name, nested_fields in parsed_fields.items():
#             full_field_name = f"{prefix}{field_name}"

#             if field_name == "*":
#                 continue

#             # Check if the field itself is allowed
#             if field_name not in allowed_fields:
#                 invalid.append(full_field_name)
#                 continue

#             # 4. If there are nested fields (and it's NOT a wildcard '*'), recurse
#             if nested_fields and nested_fields != "*":
#                 next_serializer = None
#                 next_model = None

#                 # Find the nested serializer
#                 if field_name in serializer_fields:
#                     s_field = serializer_fields[field_name]
#                     if hasattr(s_field, "child"):
#                         next_serializer = s_field.child
#                     elif hasattr(s_field, "get_fields"):
#                         next_serializer = s_field

#                 # Find the related Django model
#                 if current_model:
#                     try:
#                         m_field = current_model._meta.get_field(field_name)
#                         if m_field.is_relation and hasattr(m_field, "related_model"):
#                             next_model = m_field.related_model
#                     except FieldDoesNotExist:
#                         pass

#                 # Recurse deeper passing the string (e.g., "id,genders")
#                 invalid.extend(
#                     _validate_recursive(
#                         nested_fields, current_serializer=next_serializer, current_model=next_model, prefix=f"{full_field_name}."
#                     )
#                 )

#         return invalid

#     invalid_fields = _validate_recursive(field_list, current_serializer=serializer_class, current_model=model_class)
#     return sorted(invalid_fields)


# <<---------------------------------- Validate Query Params ----------------------------------->>
def validate_query_params(
    request, query_filter: dict | None = None, query_type="list", extended_fields: list[str] | None = None
) -> tuple[list[str], list[str]]:
    """
    Validate query params from request.

    Args:
        request: DRF request object
        query_filter: dict mapping valid query param keys to model fields
        extra_valid_fields: additional fields to consider valid

    Returns:
        tuple:
            valid_params: list of keys that are valid
            invalid_params: list of keys that are invalid
    """
    if query_type == "list":
        # Default query params always allowed
        default_fields = {"field_list", "from_date", "to_date", "search", "limit", "offset", "ordering"}
    elif query_type == "retrieve":
        # Default query params always allowed
        default_fields = {"field_list"}

    elif query_type == "create":
        # Default query params always allowed
        default_fields = {}

    # Combine defaults + query_filter keys + extra valid fields
    valid_fields = set(default_fields) | set(query_filter.keys()) if query_filter else set(default_fields)
    if extended_fields:
        valid_fields |= set(extended_fields)

    # Extract params from request
    provided_fields = set(request.query_params.keys())

    # Determine valid and invalid
    valid_params = list(valid_fields)
    invalid_params = list(provided_fields - valid_fields)

    return valid_params, invalid_params


# <<---------------------------------- Validate Ordering Fields ----------------------------------->>
def validate_ordering_fields(requested_fields: str | list[str], mapping: dict[str, str]) -> list[str]:
    """
    Validates and translates frontend ordering requests into backend database fields.
    """
    # Check if the input is a comma-separated string (common in URL query params like ?ordering=name,-age)
    # If so, split it by commas, strip any accidental whitespace, and drop any empty strings.
    if isinstance(requested_fields, str):
        requested_fields = [f.strip() for f in requested_fields.split(",") if f.strip()]

    # Initialize lists to keep track of successful mappings and illegal requests
    validated_fields = []
    invalid_fields = []

    # Process each field requested by the client one by one
    for field in requested_fields:
        # Determine if the client wants descending order (indicated by a '-' prefix)
        is_descending = field.startswith("-")

        # Extract the core field name by slicing off the '-' prefix if it exists
        base_field = field[1:] if is_descending else field

        # Verify if the requested core field is permitted by checking our mapping dictionary
        if base_field in mapping:
            # Retrieve the corresponding internal backend/ORM field name
            mapped_field = mapping[base_field]

            # If the original request was descending, re-apply the '-' prefix to the new backend field
            final_field = f"-{mapped_field}" if is_descending else mapped_field

            # Add the fully translated and formatted field to our approved list
            validated_fields.append(final_field)
        else:
            # If the field is not allowed, record the exact name the user tried to use for error reporting
            invalid_fields.append(base_field)

    return {"invalid_fields": invalid_fields, "validated_fields": validated_fields}


def get_mapped_ordering(ordering_string: str | None, mapping: dict[str, str]) -> list[str]:
    """
    Extracts and maps a comma-separated ordering string to backend fields in a single pass.
    Ignores invalid fields silently.

    Example:
        >>> get_mapped_ordering("-username, id, bad_field", {"username": "user__username", "id": "id"})
        ['-user__username', 'id']
    """
    if not ordering_string:
        return []

    mapped_fields = []

    # Split the string and process each field immediately
    for field in ordering_string.split(","):
        field = field.strip()
        if not field:
            continue

        # Check for descending prefix
        is_descending = field.startswith("-")
        base_field = field[1:] if is_descending else field

        # OPTIMIZATION: Use .get() with the walrus operator (:=)
        # This performs a single O(1) dictionary lookup instead of checking 'if base_field in mapping'
        if backend_field := mapping.get(base_field):
            mapped_fields.append(f"-{backend_field}" if is_descending else backend_field)

    return mapped_fields
