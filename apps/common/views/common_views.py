# apps/common/views.py
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from apps.common.error_codes import NOT_FOUND_ERROR

logger = logging.getLogger(__name__)


@csrf_exempt
def custom_404_handler(request, exception=None):
    """
    Standardized JSON 404 response for unresolved URLs.
    Replaces Django's default HTML 404 page.
    """
    logger.warning(f"404 Not Found: {request.path}")

    # Create a fresh dictionary for THIS request to guarantee thread-safety
    response_data = NOT_FOUND_ERROR.copy()
    response_data["data"] = {"url": request.path, "info": "The requested URL does not exist."}

    return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)
