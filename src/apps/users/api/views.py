from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenViewBase

from apps.users.api.serializers import (
    CookieTokenObtainSerializer,
    CookieTokenRefreshSerializer,
    MemberPasswordChangeSerializer,
    MemberRegistrationRequestSerializer,
    UserProfileSerializer,
)
from apps.users.models import Member
from core.throttling import AnonRateThrottle


class CookieTokenMixin(TokenViewBase):
    def finalize_response(self, request, response: Response, *args, **kwargs):
        self._store_refresh_token_in_http_cookie(response)
        return super().finalize_response(request, response, *args, **kwargs)

    def _store_refresh_token_in_http_cookie(self, response: Response):
        if response.data.get("refresh"):
            cookie_max_age = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
            response.set_cookie(
                settings.SIMPLE_JWT["REFRESH_TOKEN_COOKIE_NAME"],
                response.data["refresh"],
                max_age=cookie_max_age,
                httponly=True,
                secure=settings.SIMPLE_JWT["REFRESH_TOKEN_COOKIE_SECURE"],
                samesite=settings.SIMPLE_JWT["REFRESH_TOKEN_COOKIE_SAMESITE"],
            )
            del response.data["refresh"]


class CookieTokenObtainPairView(CookieTokenMixin, TokenObtainPairView):
    serializer_class = CookieTokenObtainSerializer
    throttle_classes = [AnonRateThrottle]

    def delete(self, request):
        response = Response(data={}, status=HTTP_204_NO_CONTENT)
        response.delete_cookie(settings.SIMPLE_JWT["REFRESH_TOKEN_COOKIE_NAME"])
        return response


class CookieTokenRefreshView(CookieTokenMixin, TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer
    throttle_classes = [AnonRateThrottle]


class MemberRegistrationRequestView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = MemberRegistrationRequestSerializer
    throttle_classes = [AnonRateThrottle]


class MemberProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = request.user
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class MemberPasswordChange(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MemberPasswordChangeSerializer

    def update(self, request, *args, **kwargs):
        instance: Member = request.user

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        if not instance.check_password(serializer.validated_data["password_current"]):
            return Response(
                {"password_current": [_("Wrong password.")]},
                status=HTTP_400_BAD_REQUEST,
            )

        if serializer.validated_data["password_new"] == serializer.validated_data["password_current"]:
            return Response(
                {"password_new": [_("New password must be different from current password.")]},
                status=HTTP_400_BAD_REQUEST,
            )

        if serializer.validated_data["password_new"] != serializer.validated_data["password_new_confirm"]:
            return Response(
                {"password_new_confirm": [_("New password and confirmation did not match.")]},
                status=HTTP_400_BAD_REQUEST,
            )

        instance.set_password(serializer.validated_data["password_new"])
        instance.save()
        return Response(status=HTTP_204_NO_CONTENT)
