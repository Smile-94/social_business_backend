# utils/logging_utils.py  (pure functions, no Django middleware coupling)
from datetime import datetime, timezone
import json
import logging

logger = logging.getLogger(__name__)

SENSITIVE_HEADERS = {
    "HTTP_AUTHORIZATION",
    "HTTP_X_CSRFTOKEN",
    "HTTP_X_CSRF_TOKEN",
    "HTTP_CSRFTOKEN",
    "HTTP_X_BROWSER_FINGERPRINT",
    "HTTP_X_DEVICE_ID",
    "HTTP_COOKIE",
}

SENSITIVE_BODY_FIELDS = {"password", "confirm_password", "token", "access", "refresh"}


def mask_sensitive_body(data):
    if isinstance(data, dict):
        return {k: "[REDACTED]" if k.lower() in SENSITIVE_BODY_FIELDS else mask_sensitive_body(v) for k, v in data.items()}
    if isinstance(data, list):
        return [mask_sensitive_body(item) for item in data]
    return data


def _extract_body(request):
    """
    Safely extract and mask the request body.
    Assumes body has already been cached by middleware before this is called.
    """
    content_type = request.META.get("CONTENT_TYPE", "").lower()

    if "multipart/form-data" in content_type or "application/x-www-form-urlencoded" in content_type:
        post_data = request.POST.dict() if hasattr(request.POST, "dict") else dict(request.POST)
        return mask_sensitive_body(post_data)

    django_request = getattr(request, "_request", request)
    stream_consumed = getattr(django_request, "_read_started", False)
    body_cached = hasattr(django_request, "_body")

    if stream_consumed and not body_cached:
        # Stream was read but not cached — unsafe to touch .body
        drf_data = getattr(request, "data", None)
        if drf_data:
            try:
                parsed = drf_data.dict() if hasattr(drf_data, "dict") else dict(drf_data)
                return mask_sensitive_body(parsed) if parsed else "[BODY ALREADY CONSUMED]"
            except Exception:
                pass
        return "[BODY ALREADY CONSUMED]"

    try:
        raw_body = django_request.body
        if not raw_body:
            return None
        if "application/json" in content_type:
            return mask_sensitive_body(json.loads(raw_body.decode("utf-8")))
        return f"[NON-JSON BODY: {content_type}]"
    except json.JSONDecodeError:
        return "[INVALID JSON BODY]"
    except Exception:
        logger.exception("Failed to read request body")
        return "[UNPARSABLE BODY]"


def _extract_headers(request):
    """Extract and redact sensitive HTTP headers."""
    headers = {k: v for k, v in request.META.items() if k.startswith("HTTP_")}
    for key in SENSITIVE_HEADERS:
        if key in headers:
            headers[key] = "[REDACTED]"
    return headers


def build_request_log_data(request, message="Request Log"):
    """
    Build a structured dict of request metadata.
    Single source of truth — used by both logging and any other consumers.
    """
    user = str(request.user) if hasattr(request, "user") and request.user.is_authenticated else "anonymous"

    return {
        "message": message,
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "user": user,
        "method": request.method,
        "path": request.path,
        "ip_address": request.META.get("REMOTE_ADDR"),
        "device": request.META.get("HTTP_USER_AGENT", "unknown"),
        "query_params": request.GET.dict(),
        "headers": _extract_headers(request),
        "body": _extract_body(request),
    }


def log_request(request, execution_time=None, message="Request Log"):
    """Log a request. Does one thing: logs. Returns nothing."""
    data = build_request_log_data(request, message)
    data["execution_time"] = execution_time

    json_data = json.dumps(data, default=str)

    logger.info(
        f"INCOMING REQUEST:------------->> {request.method} {request.path} {json_data}",
    )
