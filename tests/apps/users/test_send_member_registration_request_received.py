import pytest

from core.tasks import send_member_registration_request_received
from core.utils.mailer import Message

pytestmark = pytest.mark.django_db


def test_success(mock_mailer):
    member_id = 1

    result = send_member_registration_request_received.delay(member_id).get()

    assert result["sent"]
    message: Message = mock_mailer.send_templated_email.call_args[0][0]
    assert message.template_name == "AdminMemberRegistrationRequestReceived"
    assert message.template_data == {
        "member_admin_url": "https://example.com/admin/users/member/1/change/",
    }
