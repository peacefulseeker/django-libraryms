import pytest
import rest_framework
from django.conf import settings
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED
from rest_framework.test import APIClient

from apps.users.api.serializers import CookieTokenObtainSerializer
from apps.users.models import User

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture()
def mock_token_validate(mocker):
    return mocker.patch("rest_framework_simplejwt.serializers.TokenObtainPairSerializer.validate")


@pytest.fixture
def serializer() -> CookieTokenObtainSerializer:
    return CookieTokenObtainSerializer()


class TestTokenFromUsernameOrEmail:
    attrs = {
        "username": "member",
        "password": "member",
    }

    def test_validate_against_username(self, member, serializer):
        data = serializer.validate(self.attrs)

        assert data["access"] is not None
        assert data["refresh"] is not None

    def test_returns_user_data_along_with_token(self, member, serializer):
        data = serializer.validate(self.attrs)

        assert data["user"] == {
            "uuid": str(member.uuid),
            "username": member.username,
            "email": member.email,
            "first_name": member.first_name,
            "last_name": member.last_name,
        }

    @pytest.mark.parametrize(
        "username",
        [
            "member1",
            "",
            "notamember",
        ],
    )
    def test_raises_exception_for_wrong_email(self, serializer, username):
        attrs = {**self.attrs, "username": username}

        with pytest.raises(rest_framework.exceptions.AuthenticationFailed):
            serializer.validate(attrs)

    def test_raises_exception_for_wrong_password(self, member, serializer):
        attrs = {**self.attrs, "password": "wrongpassword"}

        with pytest.raises(rest_framework.exceptions.AuthenticationFailed):
            serializer.validate(attrs)

    def test_validate_against_email(self, member, serializer):
        attrs = {"username": "member@member.com", "password": "member"}

        data = serializer.validate(attrs)

        assert data["access"]
        assert data["refresh"]

    @pytest.mark.parametrize(
        "email",
        [
            "invalid@email.com",
            "ptc@com",
            "user@.com",
        ],
    )
    def test_validate_against_email_wrong_email(self, email, serializer):
        attrs = {**self.attrs, "email": email}

        with pytest.raises(rest_framework.exceptions.AuthenticationFailed):
            serializer.validate(attrs)

    def test_validate_against_email_wrong_password(self, member, serializer):
        attrs = {"username": "member@member.com", "password": "wrongpassword"}

        with pytest.raises(rest_framework.exceptions.AuthenticationFailed):
            serializer.validate(attrs)

    def test_ensure_original_username_field_restored_on_any_kind_of_exception(self, mock_token_validate, member, serializer):
        attrs = {"username": "member@member.com", "password": "member"}
        mock_token_validate.side_effect = Exception("any exception raised during validation")

        with pytest.raises(Exception):
            serializer.validate(attrs)

            assert User.USERNAME_FIELD == User.username.field.name


class TestCookieTokenObtain:
    url = reverse("token_obtain_pair")
    data = {
        "username": "member",
        "password": "member",
    }

    def test_access_token_obtain_from_api(self, as_member, member):
        response: Response = as_member.post(self.url, data=self.data)

        assert response.status_code == HTTP_200_OK
        assert response.data["access"]
        assert response.data["user"]
        assert not hasattr(response, "refresh")

    def test_access_token_obtain_denied_for_wrong_credentials(self, as_member):
        data = {**self.data, "password": "wrongpassword"}

        response: Response = as_member.post(self.url, data=data)

        assert response.status_code == HTTP_401_UNAUTHORIZED

    def test_access_token_obtain_denied_for_inactive_account(self, as_member, member):
        member.is_active = False
        member.save()

        response: Response = as_member.post(self.url, data=self.data)

        assert response.status_code == HTTP_401_UNAUTHORIZED

    def test_ensure_refresh_cookie_stored_as_http_only(self, as_member):
        response: Response = as_member.post(self.url, data=self.data)

        expected_cookie = response.cookies.get(settings.SIMPLE_JWT["REFRESH_TOKEN_COOKIE_NAME"])

        assert expected_cookie
        assert expected_cookie["httponly"]
        assert expected_cookie["secure"]
        assert expected_cookie["samesite"] == settings.SIMPLE_JWT["REFRESH_TOKEN_COOKIE_SAMESITE"]

    def test_refresh_cookie_delete_api(self, as_member: APIClient):
        access_response = as_member.post(self.url, data=self.data)
        expected_cookie = access_response.cookies.get(settings.SIMPLE_JWT["REFRESH_TOKEN_COOKIE_NAME"])

        assert expected_cookie
        assert expected_cookie["max-age"] > 0

        delete_response: Response = as_member.delete(self.url)

        assert delete_response.status_code == HTTP_204_NO_CONTENT
        expired_cookie = delete_response.cookies.get(settings.SIMPLE_JWT["REFRESH_TOKEN_COOKIE_NAME"])

        assert expired_cookie["max-age"] == 0
