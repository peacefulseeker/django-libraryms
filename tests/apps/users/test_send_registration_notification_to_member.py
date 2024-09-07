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

    message: Message = mock_mailer.send_templated_email.call_args[0][0]
    assert result["sent"]
    assert message.template_data == {
        "member_name": member.name,
        "member_registration_code": member.registration_code,
    }
    assert message.template_name == "MemberRegistrationNotification"


def test_template_data_includes_username(mock_mailer):
    member: Member = mixer.blend(Member, first_name="")

    send_registration_notification_to_member.delay(member.id).get()

    message: Message = mock_mailer.send_templated_email.call_args[0][0]
    assert message.template_data["member_name"] == member.username
