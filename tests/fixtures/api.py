import pytest
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def authenticated_client(client):
    def _client(user) -> APIClient:
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        client.cookies[settings.SIMPLE_JWT["REFRESH_TOKEN_COOKIE_NAME"]] = str(refresh)
        return client

    return _client


@pytest.fixture
def as_member(authenticated_client, member) -> APIClient:
    return authenticated_client(member)
