from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.business.models import BusinessRole, BusinessUser
from apps.user.models.choices import UserTypeChoices
from apps.common.helper_class.validator_class import UniqueFieldsValidatorMixin

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


# <<------------------------------------Registration Serializer---------------------------------------->>
# class BusinessRegistrationSerializer(serializers.Serializer):
#     username = serializers.CharField(max_length=100, required=False, allow_blank=True, default=None)
#     email = serializers.EmailField(required=False, allow_blank=True, default=None)
#     phone = serializers.CharField(max_length=20, required=False, allow_blank=True, default=None)
#     password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
#     confirm_password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
#     business_name = serializers.CharField(max_length=255, required=True)

#     # ─────────────────────────────────────────────────────────────────────────
#     # Object-level validation
#     # ─────────────────────────────────────────────────────────────────────────

#     def validate(self, attrs):
#         username = attrs.get("username")
#         email = attrs.get("email")
#         phone = attrs.get("phone")

#         if not any([username, email, phone]):
#             raise serializers.ValidationError({"identifier": "Provide at least one of: username, email, or phone."})

#         if attrs["password"] != attrs["confirm_password"]:
#             raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

#         return attrs

#     # ─────────────────────────────────────────────────────────────────────────
#     # Creation
#     # ─────────────────────────────────────────────────────────────────────────

#     @transaction.atomic
#     def create(self, validated_data):
#         validated_data.pop("confirm_password")
#         business_name = validated_data.pop("business_name")

#         # 1. Create the User
#         user = User.objects.create_user(
#             username=validated_data.get("username"),
#             email=validated_data.get("email"),
#             phone=validated_data.get("phone"),
#             password=validated_data["password"],
#             user_type=UserTypeChoices.BUSINESS.value,
#         )

#         # 2. Create a default owner role for this business
#         owner_role, _ = BusinessRole.objects.get_or_create(name=f"{business_name} - Owner")

#         # 3. Link user → business role
#         BusinessUser.objects.create(
#             user_id=user.pk,
#             role=owner_role,
#         )

#         # 4. Attach business metadata to the user for the response
#         user._business_name = business_name
#         user._role_name = owner_role.name
#         return user


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
