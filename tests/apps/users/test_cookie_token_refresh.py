import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED
from rest_framework.test import APIClient

from apps.users.api.serializers import CookieTokenRefreshSerializer

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def serializer() -> CookieTokenRefreshSerializer:
    return CookieTokenRefreshSerializer()


class TestCookieRefresh:
    url = reverse("token_refresh")

    def test_serializer_does_not_have_refresh_attr(self, serializer):
        assert serializer.refresh is None

    def test_grant_access_token_from_refresh_token_cookie_by_default(self, as_member):
        response: Response = as_member.post(self.url)

        assert response.status_code == HTTP_200_OK

    def test_ensure_access_token_returned_with_member_username(self, as_member, member):
        response: Response = as_member.post(self.url)

        assert response.status_code == HTTP_200_OK

        assert response.data["access"]
        assert response.data["user"] == {
            "username": member.username,
        }

    def test_deny_access_token_without_refresh_token_cookie(self, as_member):
        del as_member.cookies[settings.SIMPLE_JWT["REFRESH_TOKEN_COOKIE_NAME"]]

        response: Response = as_member.post(self.url)

        assert response.status_code == HTTP_401_UNAUTHORIZED

    def test_deny_access_token_with_wrong_token_value(self, as_member: APIClient):
        _, access_token = as_member._credentials["HTTP_AUTHORIZATION"].split(" ")
        as_member.cookies[settings.SIMPLE_JWT["REFRESH_TOKEN_COOKIE_NAME"]] = access_token

        response: Response = as_member.post(self.url)

        assert response.status_code == HTTP_401_UNAUTHORIZED
        assert str(response.data["detail"]) == "Token has wrong type"

    def test_cookie_refresh_with_user_profile(self, as_member, member):
        response: Response = as_member.post(self.url + "?fetch_user")

        assert response.data["user"] == {
            "username": member.username,
            "email": member.email,
            "first_name": member.first_name,
            "last_name": member.last_name,
        }
