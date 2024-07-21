from django.conf import settings
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.api.serializers import CookieTokenObtainSerializer, CookieTokenRefreshSerializer


class CookieTokenMixin:
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

    def delete(self, request):
        response = Response(data={}, status=HTTP_204_NO_CONTENT)
        response.delete_cookie(settings.SIMPLE_JWT["REFRESH_TOKEN_COOKIE_NAME"])
        return response


class CookieTokenRefreshView(CookieTokenMixin, TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer
