from core.tasks import send_order_created_email
from core.utils.mailer import Message


def test_send_order_created_email(mock_mailer):
    order_id = 1

    result = send_order_created_email.delay(order_id).get()

    assert result["sent"] == 1
    message: Message = mock_mailer.call_args[0][0]
    assert message.subject == "Book order created"
    assert "Hi admin!" in message.body
    assert "Please process new book order" in message.body
    assert "https://example.com/admin/books/order/1/change/" in message.body
