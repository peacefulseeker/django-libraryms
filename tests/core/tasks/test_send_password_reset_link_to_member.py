import pytest

from apps.users.models import Member
from core.tasks import send_password_reset_link_to_member

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

    mailer_kwargs = mock_mailer.call_args.kwargs
    assert mailer_kwargs["subject"] == "Password reset request"
    assert f"Hi {member_with_reset_token.first_name}!" in mailer_kwargs["body"]
    assert "You requested password reset recently." in mailer_kwargs["body"]
    assert f"https://example.com/reset-password/{member_with_reset_token.password_reset_token}" in mailer_kwargs["body"]
    assert "Link expires in 1 hour" in mailer_kwargs["body"]
    assert result["sent"] == 1
