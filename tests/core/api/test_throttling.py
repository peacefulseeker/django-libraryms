import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _enable_throttling(settings):
    settings.DISABLE_THROTTLING = False


class TestThrottling:
    url = reverse("member_registration_request")
    valid_payload = {
        "username": "john.doe",
        "email": "john.doe@example.com",
        "password": "secret_password123",
        "password_confirm": "secret_password123",
    }

    def test_throtted_response(self, client, settings):
        throttle_limit = settings.THROTTLING_ANON_RATE.split("/")[0]

        for num in range(int(throttle_limit)):
            self.valid_payload["username"] += str(num)
            self.valid_payload["email"] = str(num) + self.valid_payload["email"]
            response = client.post(self.url, self.valid_payload)
            assert response.status_code == status.HTTP_201_CREATED

        response = client.post(self.url, self.valid_payload)
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
