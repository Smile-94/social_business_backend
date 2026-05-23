import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from _library.functions.formatters import response_formatter
from apps.common.error_codes import INTERNAL_SERVER_ERROR

logger = logging.getLogger(__name__)


# Assuming you have these imported from your project, or you can use raw strings
# from your_app.constants import ErrorType, ResponseClient

logger = logging.getLogger(__name__)


def exception_handler(exc, context):
    # 1. Call REST framework's default exception handler to get standard errors
    response = drf_exception_handler(exc, context)

    # 2. Handle UNCAUGHT exceptions (Response is None -> 500 Internal Server Error)
    if response is None:
        # CRITICAL: logger.exception automatically logs the full traceback
        view_name = context.get("view").__class__.__name__ if context.get("view") else "Unknown View"
        logger.exception(f"ERROR:----------->> Unhandled Exception in {view_name}: {exc}")

        # Format the 500 response using your preferred structure
        return response_formatter(INTERNAL_SERVER_ERROR)

    response.data = {"success": False, "error": response.status_code, "detail": response.data}

    return response
