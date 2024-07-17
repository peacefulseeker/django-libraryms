import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def authenticated_client(client):
    def _client(user):
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        return client

    return _client


@pytest.fixture
def as_member(authenticated_client, member):
    return authenticated_client(member)


# @pytest.fixture
# def as_lirarian(authenticated_client, librarian):
#     return authenticated_client(librarian)
