import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestMemberPasswordChange:
    @pytest.fixture(autouse=True)
    def setup_props(self, member):
        self.url = reverse("member_password_change")
        self.payload = {
            "password_current": member.raw_password,
            "password_new": "newpassword456",
            "password_new_confirm": "newpassword456",
        }

    def test_unauthorized(self, client):
        response = client.put(self.url, self.payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_success(self, as_member, member):
        response = as_member.put(self.url, self.payload)

        member.refresh_from_db()
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert member.check_password(self.payload["password_new"])

    def test_new_password_same_as_current(self, as_member, member):
        self.payload["password_new"] = member.raw_password

        response = as_member.put(self.url, self.payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["password_new"][0] == "New password must be different from current password."

    def test_too_short_password(self, as_member):
        self.payload["password_new"] = "member"

        response = as_member.put(self.url, self.payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["password_new"][0] == "This password is too short. It must contain at least 8 characters."

    def test_wrong_old_password(self, as_member):
        self.payload["password_current"] = "wrongpassword"

        response = as_member.put(self.url, self.payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["password_current"][0] == "Wrong password."

    def test_missing_required_fields(self, as_member):
        self.payload = {"password_current": "member"}

        response = as_member.put(self.url, self.payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password_new" in response.data
        assert "password_new_confirm" in response.data

    def test_password_change_mismatch_confirm(self, as_member):
        self.payload["password_new_confirm"] = "mismatch"

        response = as_member.put(self.url, self.payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["password_new_confirm"][0] == "New password and confirmation did not match."
