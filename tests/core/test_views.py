import os
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def _create_tmp_index_template():
    # setup
    f = open("src/core/templates/vue-index.html", "w")
    yield

    # teardown
    os.remove(f.name)


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
    assert response.status_code == 200
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

        assert response.status_code == 200
        assert response.context["props"] == expected


def test_404_handler(client):
    response = client.get("/not_existing_path")
    assert response.status_code == 404
    assert response.context["props"] == {
        "error": {
            "status": 404,
            "message": "Page '/not_existing_path' not found",
        }
    }
