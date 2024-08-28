import uuid

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status


@pytest.mark.django_db
class TestMemberPasswordResetConfirmView:
    url = reverse("member_password_reset_confirm")

    @pytest.fixture
    def valid_payload(self, member_with_reset_token):
        return {
            "token": str(member_with_reset_token.password_reset_token),
            "new_password": "NewSecurePassword123!",
            "new_password_confirm": "NewSecurePassword123!",
        }

    def test_token_required(self, client, valid_payload):
        del valid_payload["token"]
        response = client.post(self.url, valid_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"token": ["This field is required."]}

    def test_passwords_required(self, client):
        response = client.post(self.url, {"token": uuid.uuid4()})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "new_password": ["This field is required."],
            "new_password_confirm": ["This field is required."],
        }

    def test_requires_valid_uuid_token(self, client, valid_payload):
        valid_payload["token"] = "not-uuid-token"

        response = client.post(self.url, valid_payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"token": ["Must be a valid UUID."]}

    def test_expired_token(self, client, member_with_reset_token, valid_payload):
        member_with_reset_token.password_reset_token_created_at = timezone.now() - timezone.timedelta(hours=2)
        member_with_reset_token.save()
        response = client.post(self.url, valid_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "Token has expired"}

    def test_no_member_found_for_given_token(self, client, member_with_reset_token, valid_payload):
        member_with_reset_token.password_reset_token = uuid.uuid4()
        member_with_reset_token.save()
        response = client.post(self.url, valid_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "Invalid token"}

    def test_password_mismatch(self, client, valid_payload):
        valid_payload["new_password_confirm"] = "DifferentPassword123!"

        response = client.post(self.url, valid_payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"new_password_confirm": ["Password fields didn't match."]}

    def test_weak_password(self, client, valid_payload):
        valid_payload["new_password"] = valid_payload["new_password_confirm"] = "weak"
        response = client.post(self.url, valid_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_reset_success(self, client, member_with_reset_token, valid_payload):
        response = client.post(self.url, valid_payload)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        member_with_reset_token.refresh_from_db()
        assert member_with_reset_token.check_password(valid_payload["new_password"])
        assert member_with_reset_token.password_reset_token is None
        assert member_with_reset_token.password_reset_token_created_at is None
