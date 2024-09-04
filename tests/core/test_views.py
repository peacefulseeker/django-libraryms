from unittest.mock import patch

import pytest
from rest_framework import status
from rest_framework.status import HTTP_200_OK


@pytest.mark.parametrize(
    "path",
    [
        "",
        "/login",
        "/books",
        "/account",
    ],
)
def test_spa_route_views(client, path):
    response = client.get(path)
    assert response.status_code == status.HTTP_200_OK
    assert response.context.template_name == "vue-index.html"
    assert response.context["props"] == {}


@pytest.mark.parametrize(
    "mock_data, expected",
    [
        ({"access": "test_token", "user": {"first_name": "mock_user"}}, {"access": "test_token", "user": {"first_name": "mock_user"}}),
        (Exception("Could not authenticate request"), {}),
    ],
)
def test_spa_view_props(client, mock_data, expected):
    with patch("core.views.CookieTokenRefreshSerializer") as mock_serializer:
        if isinstance(mock_data, Exception):
            mock_serializer.return_value.validate.side_effect = mock_data
        else:
            mock_serializer.return_value.validate.return_value = mock_data
        response = client.get("/")

        assert response.status_code == status.HTTP_200_OK
        assert response.context["props"] == expected
        assert response.context["FRONTEND_ASSETS_URL"] == "/static/frontend/"


def test_frontend_assets_url_from_env(client):
    import os

    os.environ["FRONTEND_ASSETS_VERSION"] = "timestamp_hash"
    os.environ["AWS_S3_CUSTOM_DOMAIN"] = "cdn.example.com"

    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.context["FRONTEND_ASSETS_URL"] == "https://cdn.example.com/v/timestamp_hash/"


def test_404_handler(client):
    response = client.get("/not_existing_path")
    assert response.status_code == 404
    assert response.context["props"] == {
        "error": {
            "status": 404,
            "message": "Page '/not_existing_path' not found",
        }
    }


def test_healtcheck(client):
    response = client.get("/healthz")

    assert response.status_code == HTTP_200_OK
    assert response.content == b"ok"
