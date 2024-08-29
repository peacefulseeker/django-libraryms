import pytest
from rest_framework.exceptions import APIException, Throttled
from rest_framework.views import APIView

from core.api.exceptions import drf_exception_handler


@pytest.fixture
def api_request(client):
    return client.get("/")


@pytest.fixture
def api_view():
    return APIView()


def test_drf_exception_handler_throttled(api_request, api_view):
    exc = Throttled()
    context = {"view": api_view, "request": api_request}

    response = drf_exception_handler(exc, context)

    assert response is not None
    assert response.status_code == 429
    assert "Too Many Requests" in response.data["detail"]


def test_drf_exception_handler_non_throttled(api_request, api_view):
    exc = APIException("Test exception")
    context = {"view": api_view, "request": api_request}

    response = drf_exception_handler(exc, context)

    assert response is not None
    assert response.status_code == 500
    assert "detail" in response.data
    assert "Too Many Requests" not in response.data["detail"]


def test_drf_exception_handler_non_drf_exception(api_request, api_view):
    exc = ValueError("Some random exception")
    context = {"view": api_view, "request": api_request}

    response = drf_exception_handler(exc, context)

    assert response is None
