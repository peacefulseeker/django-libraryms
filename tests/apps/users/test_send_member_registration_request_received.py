import pytest

from core.tasks import send_member_registration_request_received
from core.utils.mailer import Message

pytestmark = pytest.mark.django_db


def test_success(mock_mailer):
    member_id = 1

    result = send_member_registration_request_received.delay(member_id).get()

    assert result["sent"]
    message: Message = mock_mailer.call_args[0][0]
    assert message.subject == "Registration request received"
    assert "Hi admin!" in message.body
    assert "New member registration request received" in message.body
    assert "https://example.com/admin/users/member/1/change/" in message.body
