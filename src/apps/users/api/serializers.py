from typing import Any, Dict

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.fields import Field
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken

from apps.users.models import Member, User
from core.tasks import send_member_registration_request_received, send_registration_notification_to_member


class UsernameSerializer(serializers.ModelSerializer):
    "Only member username supposed to be returned alogn with access token by default"

    class Meta:
        model = User
        fields = ("username",)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")


class CookieTokenSerializerMixin:
    context: Field.context

    @property
    def should_fetch_user(self) -> bool:
        if "request" not in self.context:
            return False

        return "fetch_user" in self.context["request"].GET

    def get_user_serializer(self, user: User) -> type[UserProfileSerializer | UsernameSerializer]:
        if self.should_fetch_user:
            return UserProfileSerializer(user)
        return UsernameSerializer(user)


class CookieTokenRefreshSerializer(CookieTokenSerializerMixin, TokenRefreshSerializer):
    refresh = None

    def validate(self, attrs: dict = {}) -> Dict[str, Any]:
        attrs["refresh"] = self.context["request"].COOKIES.get(settings.SIMPLE_JWT["REFRESH_TOKEN_COOKIE_NAME"])
        if attrs["refresh"]:
            data = super().validate(attrs)
            return self.access_token_with_user(data)
        else:
            raise InvalidToken()

    def access_token_with_user(self, data: dict) -> dict:
        access = AccessToken(data["access"])
        user = User.objects.get(id=access["user_id"])
        user_serializer = self.get_user_serializer(user)
        data["user"] = user_serializer.data
        return data


class CookieTokenObtainSerializer(CookieTokenSerializerMixin, TokenObtainPairSerializer):
    user: User

    def validate(self, attrs: dict) -> dict:
        if "@" in attrs["username"]:
            data = self.validate_against_email(attrs)
        else:
            data = super().validate(attrs)
        return self.access_token_with_user(data)

    def access_token_with_user(self, data: dict) -> dict:
        user_serializer = self.get_user_serializer(self.user)
        data["user"] = user_serializer.data
        return data

    def validate_against_email(self, attrs: dict) -> dict:
        """
        Temporarily swaps USERNAME_FIELD with email field, so default
        django auth backend can use that for authenticating the user against email.
        Afterwards restoring that back to original USERNAME_FIELD
        """
        original_username_field = User.USERNAME_FIELD
        User.USERNAME_FIELD = User.EMAIL_FIELD

        attrs[User.EMAIL_FIELD] = attrs.pop("username")
        self.username_field = User.USERNAME_FIELD

        try:
            data = super().validate(attrs)
        except:
            User.USERNAME_FIELD = original_username_field
            raise

        User.USERNAME_FIELD = original_username_field

        return data


class MemberRegistrationRequestSerializer(serializers.ModelSerializer):
    PASSWORD_MISMATCH_ERROR = _("Password fields didn't match.")

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = Member
        fields = ("uuid", "username", "email", "first_name", "last_name", "password", "password_confirm")

    def validate(self, attrs: dict) -> dict:
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password": self.PASSWORD_MISMATCH_ERROR})
        return super().validate(attrs)

    def to_representation(self, instance: Member) -> dict:
        return {"registration_code": instance.registration_code}

    def create(self, validated_data: dict) -> Member:
        member = Member.objects.create_user(
            is_active=False,
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            password=validated_data["password"],
        )
        send_member_registration_request_received.delay(member.id)
        send_registration_notification_to_member.delay(member.id)
        return member


class MemberPasswordChangeSerializer(serializers.Serializer):
    password_current = serializers.CharField(write_only=True, required=True)
    password_new = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_new_confirm = serializers.CharField(write_only=True, required=True, validators=[validate_password])


class MemberPasswordResetSerializer(serializers.Serializer):
    email = serializers.CharField(write_only=True, required=True)


class MemberPasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True, validators=[validate_password])

    def validate(self, attrs: dict[str, Any]) -> dict:
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": _("Password fields didn't match.")})
        return attrs
