import uuid

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.users.models import Member


@pytest.mark.django_db
class TestMemberRegistrationRequestView:
    url = reverse("member_password_reset")

    @pytest.fixture(autouse=True)
    def mock_send_password_reset_link_to_member(self, mocker):
        return mocker.patch("apps.users.api.views.send_password_reset_link_to_member")

    @pytest.fixture
    def valid_payload(self, member):
        return {
            "email": member.email,
        }

    def test_email_required(self, client):
        response = client.post(self.url, {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"email": ["This field is required."]}

    def test_reset_link_sent_to_member(self, member, client, valid_payload, mock_send_password_reset_link_to_member):
        response = client.post(self.url, valid_payload)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        member.refresh_from_db()
        assert member.password_reset_token is not None
        assert member.password_reset_token_created_at is not None

        assert mock_send_password_reset_link_to_member.called_once_with(member.id)

    def test_member_is_not_found(self, client, valid_payload, mock_send_password_reset_link_to_member):
        valid_payload["email"] = "not-a-member@member.com"

        response = client.post(self.url, valid_payload)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert mock_send_password_reset_link_to_member.not_called()

    def test_same_password_reset_token_used_if_not_expired(self, member, client, valid_payload):
        client.post(self.url, valid_payload)

        member.refresh_from_db()
        member_reset_token_initial = member.password_reset_token
        assert member_reset_token_initial is not None

        client.post(self.url, valid_payload)

        member.refresh_from_db()
        assert member.password_reset_token == member_reset_token_initial

    def test_new_token_generated_in_case_current_expired(self, member: Member, client, valid_payload):
        current_token = member.password_reset_token = uuid.uuid4()
        member.password_reset_token_created_at = timezone.now() - timezone.timedelta(days=1)
        member.save()
        assert not member.is_password_reset_token_valid()

        client.post(self.url, valid_payload)

        member.refresh_from_db()

        assert member.password_reset_token != current_token
        assert member.is_password_reset_token_valid()
