from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.authentication.serializers.authentication_serializers import (
    BusinessRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    RegistrationResponseSerializer,
    UserResponseSerializer,
)


# <<------------------------------------Register View---------------------------------------->>
class BusinessRegisterView(APIView):
    """
    POST /api/auth/register/

    Creates a new business owner account and returns JWT tokens immediately
    so the user is logged in right after registration.

    Request body:
        {
            "username":      "john_doe",        # optional – at least one identifier required
            "email":         "john@acme.com",   # optional
            "phone":         "+8801700000000",  # optional
            "password":      "Str0ng!Pass",
            "confirm_password": "Str0ng!Pass",
            "business_name": "Acme Corp"
        }

    Response 201:
        {
            "access":  "<jwt-access-token>",
            "refresh": "<jwt-refresh-token>",
            "user": { ... }
        }
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = BusinessRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        # Issue tokens right away — no extra login step needed
        refresh = RefreshToken.for_user(user)
        # Inject custom claims (mirrors CustomTokenObtainPairSerializer)
        refresh["username"] = user.username
        refresh["email"] = user.email
        refresh["user_type"] = user.user_type
        refresh["is_staff"] = user.is_staff

        response_data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserResponseSerializer(user).data,
        }

        return Response(
            RegistrationResponseSerializer(response_data).data,
            status=status.HTTP_201_CREATED,
        )


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
