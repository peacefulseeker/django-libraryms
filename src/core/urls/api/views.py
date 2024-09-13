from drf_spectacular.views import SpectacularSwaggerView
from rest_framework.request import Request
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from apps.users.api.serializers import CookieTokenRefreshSerializer
from core.permissions import IsSuperUser


class AuthenticatedSpectacularSwaggerView(SpectacularSwaggerView):
    permission_classes = [IsSuperUser]

    def perform_authentication(self, request: Request) -> Request.user:
        try:
            data = CookieTokenRefreshSerializer(context={"request": self.request}).validate()
            request.META["HTTP_AUTHORIZATION"] = f"Bearer {data['access']}"
        except (InvalidToken, TokenError):
            raise self.permission_denied(request)
