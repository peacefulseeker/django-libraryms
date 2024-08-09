from unittest.mock import patch

import requests

from core.tasks import ping_production_website


@patch("core.tasks.requests.get")
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


@patch("core.tasks.requests.get")
def test_ping_production_website_failure(mock_get):
    # Setup
    mock_get.side_effect = requests.exceptions.RequestException("Connection error")

    # Execute
    result = ping_production_website.delay().get()

    # Assert
    assert "error" in result
    assert "Connection error" in result["error"]


@patch("core.tasks.requests.get")
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
