from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.business.models import BusinessRole, BusinessUser
from apps.user.models.choices import UserTypeChoices
from apps.common.helper_class.validator_class import UniqueFieldsValidatorMixin
from apps.common.helper_class.password_match import PasswordMatchValidator

User = get_user_model()


# <<------------------------------------Custom Token Claim---------------------------------------->>
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends the default JWT payload with extra user claims so the frontend
    never needs a separate /me call after login.
    """

    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)
        token["username"] = user.username
        token["email"] = user.email
        token["user_type"] = user.user_type
        token["is_staff"] = user.is_staff
        return token

    def validate(self, attrs):
        # USERNAME_FIELD is 'username', but allow login with email too
        login_field = attrs.get("username", "").strip()
        password = attrs.get("password", "")

        user = None

        # Try email first if the value looks like an email
        if "@" in login_field:
            user = User.objects.filter(email=login_field, is_active=True, is_deleted=False).first()
        else:
            user = User.objects.filter(username=login_field, is_active=True, is_deleted=False).first()

        if user is None or not user.check_password(password):
            raise serializers.ValidationError({"detail": "No active account found with the given credentials."})

        refresh = self.get_token(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class BusinessRegistrationSerializer(UniqueFieldsValidatorMixin, serializers.Serializer):
    username = serializers.CharField(max_length=100, required=True)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(max_length=20, required=True)
    password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
    confirm_password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
    unique_validator_model = User
    unique_fields = ["username", "email", "phone"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs = PasswordMatchValidator()(attrs)

        return attrs


# <<------------------------------------Response Serializers---------------------------------------->>
class UserResponseSerializer(serializers.ModelSerializer):
    """Read-only snapshot returned after register / login."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "phone", "user_type", "is_active", "created_at"]
        read_only_fields = fields


class RegistrationResponseSerializer(serializers.Serializer):
    """Wraps tokens + user data in the register response."""

    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserResponseSerializer()
