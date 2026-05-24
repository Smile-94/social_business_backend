def get_field_list_from_request(request):
    """
    Extract and normalize `field_list` from request query params.

    Supported:
    - ?field_list=*              → "*"
    - ?field_list=id,name,slug   → ["id", "name", "slug"]
    - missing / empty            → "*"

    Returns:
        list[str] | str
    """
    field_list_param = request.query_params.get("field_list")

    if not field_list_param:
        return "*"

    field_list_param = field_list_param.strip()

    if field_list_param == "*":
        return "*"

    return [field.strip() for field in field_list_param.split(",") if field.strip()]


def get_supported_field_list_string(serializer_class) -> str:
    """
    Return a comma-separated string of supported fields
    from a DRF Serializer or ModelSerializer, including nested fields.

    Example Output:
        "id, employee_id, user(id, email), address(id, city, state)"
    """
    if not serializer_class:
        return ""

    def _get_nested_fields(serializer_instance):
        field_strings = []

        # get_fields() evaluates all fields defined on the serializer
        for field_name, field in serializer_instance.get_fields().items():
            # 1. Handle One-to-One / ForeignKey nested serializers (e.g., profile=ProfileSerializer())
            if hasattr(field, "fields"):
                nested_fields = ", ".join(_get_nested_fields(field))
                field_strings.append(f"{field_name}({nested_fields})")

            # 2. Handle Many-to-Many / Reverse FK nested serializers (e.g., address=AddressSerializer(many=True))
            # DRF wraps many=True in a ListSerializer, so we must check field.child
            elif hasattr(field, "child") and hasattr(field.child, "fields"):
                nested_fields = ", ".join(_get_nested_fields(field.child))
                field_strings.append(f"{field_name}({nested_fields})")

            # 3. Handle standard flat fields (e.g., IntegerField, CharField)
            else:
                field_strings.append(field_name)

        return field_strings

    # Initialize an empty serializer to inspect its fields safely
    serializer = serializer_class()

    # Build and return the final comma-separated string
    return ", ".join(_get_nested_fields(serializer))


# def get_supported_field_list_string(serializer_class) -> str:
#     """
#     Return a comma-separated string of supported fields
#     from a DRF Serializer or ModelSerializer.

#     Example:
#         "id,name,slug,created_at"
#     """
#     if not serializer_class:
#         return ""

#     serializer = serializer_class()
#     fields = serializer.get_fields().keys()

#     return ",".join(fields)
