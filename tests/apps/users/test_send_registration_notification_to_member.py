import pytest
from mixer.backend.django import mixer

from apps.users.models import Member
from core.tasks import send_registration_notification_to_member

pytestmark = pytest.mark.django_db


def test_send_member_does_not_exist():
    member_id = 1

    result = send_registration_notification_to_member.delay(member_id).get()

    assert result["error"] == f"Member with id {member_id} does not exist"


def test_send_success_with_first_name_in_greeting(mock_mailer):
    member: Member = mixer.blend(Member)

    result = send_registration_notification_to_member.delay(member.id).get()

    assert result["sent"]
    call_kwargs = mock_mailer.call_args.kwargs
    assert call_kwargs["subject"] == "Thanks! Your registration request received"
    assert f"Hi {member.first_name}!" in call_kwargs["body"]
    assert f"Your registration code: {member.registration_code}." in call_kwargs["body"]
    assert "Please arrive to library to complete registration" in call_kwargs["body"]
    assert "Don't forget to bring your ID card." in call_kwargs["body"]


def test_send_success_with_username_in_greeting(mock_mailer):
    member: Member = mixer.blend(Member, first_name="")

    send_registration_notification_to_member.delay(member.id).get()

    assert f"Hi {member.username}!" in mock_mailer.call_args.kwargs["body"]
