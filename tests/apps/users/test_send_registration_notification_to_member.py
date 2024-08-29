import pytest
from mixer.backend.django import mixer

from apps.users.models import Member
from core.tasks import send_registration_notification_to_member
from core.utils.mailer import Message

pytestmark = pytest.mark.django_db


def test_send_member_does_not_exist():
    member_id = 1

    result = send_registration_notification_to_member.delay(member_id).get()

    assert result["error"] == f"Member with id {member_id} does not exist"


def test_send_success_with_first_name_in_greeting(mock_mailer):
    member: Member = mixer.blend(Member)

    result = send_registration_notification_to_member.delay(member.id).get()

    assert result["sent"]
    message: Message = mock_mailer.call_args[0][0]
    assert message.subject == "Thanks! Your registration request received"
    assert f"Hi {member.first_name}!" in message.body
    assert f"Your registration code: {member.registration_code}." in message.body
    assert "Please arrive to library to complete registration" in message.body
    assert "Don't forget to bring your ID card." in message.body


def test_send_success_with_username_in_greeting(mock_mailer):
    member: Member = mixer.blend(Member, first_name="")

    send_registration_notification_to_member.delay(member.id).get()

    message: Message = mock_mailer.call_args[0][0]
    assert f"Hi {member.username}!" in message.body
