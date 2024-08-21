import pytest

from core.tasks import send_member_registration_request_received

pytestmark = pytest.mark.django_db


def test_success(mock_mailer):
    member_id = 1

    result = send_member_registration_request_received.delay(member_id).get()

    assert result["sent"]
    call_kwargs = mock_mailer.call_args.kwargs
    assert call_kwargs["subject"] == "Registration request received"
    assert "Hi admin!" in call_kwargs["body"]
    assert "New member registration request received" in call_kwargs["body"]
    assert "https://example.com/admin/users/member/1/change/" in call_kwargs["body"]
