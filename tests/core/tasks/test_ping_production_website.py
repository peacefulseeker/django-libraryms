import pytest
import requests

from core.tasks import ping_production_website


@pytest.fixture
def mock_get(mocker):
    return mocker.patch("core.tasks.requests.get")


def test_ping_production_website_success(mock_get):
    # Setup
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.elapsed.total_seconds.return_value = 0.5

    # Execute
    result = ping_production_website.delay().get()

    # Assert
    assert result["status"] == 200
    assert result["response_time"] == 0.5
    assert result["url"] == "https://example.com"  # defined in pyproject pytest env


def test_ping_production_website_failure(mock_get):
    # Setup
    mock_get.side_effect = requests.exceptions.RequestException("Connection error")

    # Execute
    result = ping_production_website.delay().get()

    # Assert
    assert "error" in result
    assert "Connection error" in result["error"]


def test_ping_production_website_custom_url(mock_get):
    # Setup
    custom_url = "https://custom-url.com"
    mock_response = mock_get.return_value
    mock_response.status_code = 200

    # Execute
    result = ping_production_website.delay(url=custom_url).get()

    # Assert
    assert result["url"] == custom_url
    mock_get.assert_called_once_with(custom_url, headers={"User-Agent": "DjangoLibraryMS/CeleryBeat"})


def test_ping_production_website_error_captured_by_sentry(mocker, mock_get):
    # Setup
    mock_capture_exception = mocker.patch("core.tasks.capture_exception")
    mock_get.side_effect = requests.exceptions.RequestException("Ooops, something went wrong")

    # Execute
    ping_production_website.delay().get()

    # Verify the captured exception
    mock_capture_exception.assert_called_once()
    args, kwargs = mock_capture_exception.call_args
    assert isinstance(args[0], requests.exceptions.RequestException)
    assert str(args[0]) == "Ooops, something went wrong"
