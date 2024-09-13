import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework import status as status_codes

url = reverse("swagger-ui")

pytestmark = pytest.mark.django_db


def test_auth_required(client):
    response = client.get(url)

    assert response.status_code == status_codes.HTTP_401_UNAUTHORIZED


def test_invalid_expired_token_auth_required(client):
    client.cookies[settings.SIMPLE_JWT["REFRESH_TOKEN_COOKIE_NAME"]] = "wrong_token"
    response = client.get(url)

    assert response.status_code == status_codes.HTTP_401_UNAUTHORIZED


def test_view_as_admin_superuser_with_valid_token_allowed(as_admin_client):
    response = as_admin_client.get(url)

    assert response.status_code == status_codes.HTTP_200_OK


def test_view_as_member_with_valid_token_forbidden(as_member):
    response = as_member.get(url)

    assert response.status_code == status_codes.HTTP_403_FORBIDDEN


def test_view_as_librarian_staff_with_valid_token_forbidden(as_librarian_staff_client):
    response = as_librarian_staff_client.get(url)

    assert response.status_code == status_codes.HTTP_403_FORBIDDEN
