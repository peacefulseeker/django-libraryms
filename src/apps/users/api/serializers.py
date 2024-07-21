from django.conf import settings
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken

from apps.users.models import User
from apps.users.types import AuthAttrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "uuid",
            "username",
            "email",
            "first_name",
            "last_name",
        )


class CookieTokenRefreshSerializer(TokenRefreshSerializer):
    refresh = None

    def validate(self, attrs):
        attrs["refresh"] = self.context["request"].COOKIES.get(settings.SIMPLE_JWT["REFRESH_TOKEN_COOKIE_NAME"])
        if attrs["refresh"]:
            data = super().validate(attrs)
            return self.access_token_with_user(data)
        else:
            raise InvalidToken(f"No refresh token presents in {settings.SIMPLE_JWT['REFRESH_TOKEN_COOKIE_NAME']} cookie")

    def access_token_with_user(self, data):
        access = AccessToken(data["access"])
        user = User.objects.get(id=access["user_id"])
        user_serializer = UserSerializer(user)
        data["user"] = user_serializer.data
        return data


class CookieTokenObtainSerializer(TokenObtainPairSerializer):
    user: User

    def validate(self, attrs: AuthAttrs):
        if "@" in attrs["username"]:
            data = self.validate_against_email(attrs)
        else:
            data = super().validate(attrs)
        return self.access_token_with_user(data)

    def access_token_with_user(self, data):
        user_serializer = UserSerializer(self.user)
        data["user"] = user_serializer.data
        return data

    def validate_against_email(self, attrs):
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
