import pytest
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture(scope="session")
def client() -> APIClient:
    return APIClient()


@pytest.fixture
def authenticated_client(client: APIClient):
    def _client(user) -> APIClient:
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        client.cookies[settings.SIMPLE_JWT["REFRESH_TOKEN_COOKIE_NAME"]] = str(refresh)
        return client

    yield _client

    client.logout()


@pytest.fixture
def as_member(authenticated_client, member) -> APIClient:
    return authenticated_client(member)


@pytest.fixture
def as_another_member(authenticated_client, another_member) -> APIClient:
    return authenticated_client(another_member)


@pytest.fixture
def as_admin(client, admin_user) -> APIClient:
    client.force_login(user=admin_user)
    return client


@pytest.fixture
def as_librarian_staff(client, librarian_staff) -> APIClient:
    client.force_login(user=librarian_staff)
    return client
