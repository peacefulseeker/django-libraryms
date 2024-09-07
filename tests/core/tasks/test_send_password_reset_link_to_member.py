import pytest

from apps.users.models import Member
from core.tasks import send_password_reset_link_to_member
from core.utils.mailer import Message

pytestmark = pytest.mark.django_db


def test_member_does_not_exist():
    member_id = 1

    result = send_password_reset_link_to_member.delay(member_id).get()

    assert result == {"error": f"Member with id {member_id} does not exist"}


def test_ensures_valid_reset_token_before_sent(member: Member):
    assert not member.is_password_reset_token_valid()

    send_password_reset_link_to_member.delay(member.id).get()

    member.refresh_from_db()
    assert member.is_password_reset_token_valid()


def test_email_sent(member_with_reset_token, mock_mailer):
    result = send_password_reset_link_to_member.delay(member_with_reset_token.id).get()

    assert result["sent"] == 1
    message: Message = mock_mailer.send_templated_email.call_args[0][0]
    assert message.template_name == "MemberPasswordResetLink"
    assert message.template_data == {
        "member_name": member_with_reset_token.name,
        "password_reset_url": f"https://example.com/reset-password/{member_with_reset_token.password_reset_token}",
    }
