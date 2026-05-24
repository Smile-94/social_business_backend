from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from _library.functions.formatters import response_formatter
from apps.authentication.serializers.authentication_serializers import (
    BusinessRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    RegistrationResponseSerializer,
    UserResponseSerializer,
)
from apps.authentication.services.authentication_services import BusinessUserService
from apps.common.error_codes import BAD_REQUEST_DEVELOPER_ERROR, CONFLICT_ERROR
from apps.common.helper_class.exceptions import ConflictError, ServiceValidationError
from apps.common.helper_class.request_validator import RequestValidator


# <<------------------------------------Register View---------------------------------------->>
class BusinessRegisterView(APIView):
    permission_classes = [AllowAny]

    model_class = User
    service_class = BusinessUserService
    request_validator = RequestValidator
    serializer_class = BusinessRegistrationSerializer
    response_serializer = RegistrationResponseSerializer

    def post(self, request, *args, **kwargs):
        #
        error = self.request_validator.validate_empty_data(request, self.serializer_class, caller=self)
        if error:
            return error

        error = self.request_validator.validate_invalid_fields(self.model_class, request.data, self.serializer_class, caller=self)
        if error:
            return error

        serializer = self.serializer_class(data=request.data)
        error = self.request_validator.validate_serializer(serializer, caller=self)
        if error:
            return error

        try:
            service = self.service_class()
            result = service.create_user(
                serializer.validated_data,
                action_user=request.user,
            )
        except ConflictError as exc:
            return response_formatter(CONFLICT_ERROR, {"message": str(exc)})
        except ServiceValidationError as exc:
            return response_formatter(BAD_REQUEST_DEVELOPER_ERROR, {"message": str(exc)})

        # refresh = RefreshToken.for_user(user)
        # refresh["username"] = user.username
        # refresh["email"] = user.email
        # refresh["user_type"] = user.user_type
        # refresh["is_staff"] = user.is_staff

        # response_data = {
        #     "access": str(refresh.access_token),
        #     "refresh": str(refresh),
        #     "user": UserResponseSerializer(user).data,
        # }

        # return Response(
        #     RegistrationResponseSerializer(response_data).data,
        #     status=status.HTTP_201_CREATED,
        # )
        return Response(result.user.pk, status=status.HTTP_201_CREATED)


# <<------------------------------------Login View---------------------------------------->>
class BusinessLoginView(TokenObtainPairView):
    """
    POST /api/auth/login/

    Accepts username OR email in the 'username' field (handled by the
    custom serializer), plus 'password'.

    Request body:
        { "username": "john@acme.com", "password": "Str0ng!Pass" }
        { "username": "john_doe",      "password": "Str0ng!Pass" }

    Response 200:
        { "access": "...", "refresh": "..." }
    """

    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


# <<------------------------------------Token Refresh View---------------------------------------->>
class TokenRefreshViewExtended(TokenRefreshView):
    """
    POST /api/auth/token/refresh/

    Standard Simple JWT refresh — included here so it lives under the same
    URL namespace and can be overridden later if needed.
    """

    permission_classes = [AllowAny]


# <<------------------------------------Logout View---------------------------------------->>
class LogoutView(APIView):
    """
    POST /api/auth/logout/

    Blacklists the refresh token so it can no longer be used.
    Requires 'rest_framework_simplejwt.token_blacklist' in INSTALLED_APPS
    and running: python manage.py migrate

    Request body:
        { "refresh": "<refresh-token>" }
    """

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {"detail": "Token is invalid or already blacklisted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
