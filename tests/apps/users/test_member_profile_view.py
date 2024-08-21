import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestMemberRegistrationRequestView:
    url = reverse("member_profile")

    def test_denied_for_unauthenticated_user(self, client):
        response = client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_profile_returned(self, as_member, member):
        response = as_member.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "username": member.username,
            "email": member.email,
            "first_name": member.first_name,
            "last_name": member.last_name,
        }
