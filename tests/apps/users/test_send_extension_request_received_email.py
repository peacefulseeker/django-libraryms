import pytest

from core.tasks import send_extension_request_received_email
from core.utils.mailer import Message

pytestmark = pytest.mark.django_db


def test_success(mock_mailer):
    extension_id = 1

    result = send_extension_request_received_email.delay(extension_id).get()

    assert result["sent"]
    message: Message = mock_mailer.send_templated_email.call_args[0][0]
    assert message.template_name == "AdminReservationExtensionRequested"
    assert message.template_data == {
        "extension_admin_url": "https://example.com/admin/books/reservationextension/1/change/",
    }
