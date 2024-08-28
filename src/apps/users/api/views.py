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
    MemberPasswordResetConfirmSerializer,
    MemberPasswordResetSerializer,
    MemberRegistrationRequestSerializer,
    UserProfileSerializer,
)
from apps.users.models import InvalidPasswordResetTokenError, Member
from core.tasks import send_password_reset_link_to_member
from core.throttling import AnonRateThrottle, PasswordResetConfirmRateThrottle, PasswordResetRateThrottle


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


class MemberPasswordReset(generics.GenericAPIView):
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]
    serializer_class = MemberPasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            member = Member.objects.get(email=serializer.validated_data["email"])
            member.set_password_reset_token()
            send_password_reset_link_to_member.delay(member.id)
            return Response(status=HTTP_204_NO_CONTENT)
        except Member.DoesNotExist:
            pass

        return Response(status=HTTP_204_NO_CONTENT)


class MemberPasswordResetConfirm(generics.GenericAPIView):
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetConfirmRateThrottle]
    serializer_class = MemberPasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            member = Member.objects.get(password_reset_token=serializer.validated_data["token"])
            member.is_password_reset_token_valid(raise_exception=True)
            member.set_password(serializer.validated_data["new_password"])
            member.password_reset_token = None
            member.password_reset_token_created_at = None
            member.save()
            return Response(status=HTTP_204_NO_CONTENT)
        except Member.DoesNotExist:
            return Response({"error": "Invalid token"}, status=HTTP_400_BAD_REQUEST)
        except InvalidPasswordResetTokenError as e:
            return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)
