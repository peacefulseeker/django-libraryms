import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from apps.users.api.serializers import MemberRegistrationRequestSerializer
from apps.users.models import Member


@pytest.mark.django_db
class TestMemberRegistrationRequestView:
    url = reverse("member_registration_request")

    @pytest.fixture(autouse=True)
    def mock_send_member_registration_request_received(self, mocker):
        return mocker.patch("src.apps.users.api.serializers.send_member_registration_request_received")

    @pytest.fixture(autouse=True)
    def mock_send_registration_notification_to_member(self, mocker):
        return mocker.patch("src.apps.users.api.serializers.send_registration_notification_to_member")

    @pytest.fixture
    def valid_payload(self):
        return {
            "username": "newmember",
            "email": "newmember@example.com",
            "password": "securepassword123",
            "password_confirm": "securepassword123",
            "first_name": "New",
            "last_name": "Member",
        }

    @pytest.fixture
    def _register_member(self, client, valid_payload) -> Response:
        return client.post(self.url, valid_payload)

    def test_success_registration_code_returned(self, client, valid_payload):
        response = client.post(self.url, valid_payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert "registration_code" in response.data

    def test_success_registration_member_props(self, client, valid_payload):
        response = client.post(self.url, valid_payload)

        assert response.status_code == status.HTTP_201_CREATED

        member = Member.objects.get(email=valid_payload["email"])
        assert not member.is_active
        assert member.username == valid_payload["username"]
        assert member.check_password(valid_payload["password"])
        assert member.first_name == valid_payload["first_name"]
        assert member.last_name == valid_payload["last_name"]
        assert member.email == valid_payload["email"]

    def test_success_first_name_last_name_optional(self, client, valid_payload):
        del valid_payload["first_name"]
        del valid_payload["last_name"]

        client.post(self.url, valid_payload)

        member = Member.objects.get(email=valid_payload["email"])

        assert member.first_name == ""
        assert member.last_name == ""

    def test_unique_username_and_email_validation_fails(self, _register_member, client, valid_payload):
        response = client.post(self.url, valid_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data["username"][0]) == Member.username.field.error_messages["unique"]
        assert str(response.data["email"][0]) == Member.email.field.error_messages["unique"]

    def test_unique_username_and_email_validation_succeeds(self, _register_member, client, valid_payload):
        member_created_response: Response = _register_member

        valid_payload["username"] = "anothermember"
        valid_payload["email"] = "anothermember@example.com"

        response: Response = client.post(self.url, valid_payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["registration_code"] != member_created_response.data["registration_code"]

    def test_password_confirmation_mismatch(self, client, valid_payload):
        valid_payload["password_confirm"] = "anotherpassword"

        response = client.post(self.url, valid_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data["password"][0]) == MemberRegistrationRequestSerializer.PASSWORD_MISMATCH_ERROR

    def test_notification_emails_sent_to_admin_and_member(
        self, _register_member, mock_send_member_registration_request_received, mock_send_registration_notification_to_member, valid_payload
    ):
        member = Member.objects.get(email=valid_payload["email"])
        assert mock_send_member_registration_request_received.delay.called_once_with(member.id)
        assert mock_send_registration_notification_to_member.delay.called_once_with(member.id)
