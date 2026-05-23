import logging
import time

from django.utils.deprecation import MiddlewareMixin

from apps.common.functions.request_logging import log_request

logger = logging.getLogger(__name__)


logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Logs every incoming request.

    Responsibilities (and only these):
      1. Cache the request body before the stream is consumed by a view.
      2. Delegate logging to log_request().
      3. Pass the request through unchanged.
    """

    def process_request(self, request):
        """Cache body early, before any view or DRF parser can consume the stream."""
        request._log_start_time = time.perf_counter()
        self._try_cache_body(request)

    def process_response(self, request, response):
        try:
            start = getattr(request, "_log_start_time", None)
            execution_time = self._format_execution_time(start) if start is not None else "unknown"
            log_request(request, execution_time=execution_time)
        except Exception:
            logger.exception("RequestLoggingMiddleware failed to log request")
        return response

    @staticmethod
    def _try_cache_body(request):
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return
        content_type = request.META.get("CONTENT_TYPE", "")
        if "multipart/form-data" in content_type:
            return
        try:
            _ = request.body  # triggers Django's internal caching into _body
        except Exception:
            logger.warning(f"ERROR------------>>Could not pre-cache request body for {request.method} {request.path}")

    def _format_execution_time(self, start: float) -> str:
        elapsed_ms = (time.perf_counter() - start) * 1000

        if elapsed_ms < 1000:
            return f"{round(elapsed_ms, 2)}ms"
        elif elapsed_ms < 60_000:
            return f"{round(elapsed_ms / 1000, 2)}s"
        else:
            return f"{round(elapsed_ms / 60_000, 2)}min"
