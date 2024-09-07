from core.tasks import send_order_created_email
from core.utils.mailer import Message


def test_send_order_created_email(mock_mailer):
    order_id = 1

    result = send_order_created_email.delay(order_id).get()

    assert result["sent"] == 1
    message: Message = mock_mailer.send_templated_email.call_args[0][0]
    assert message.template_name == "AdminOrderCreated"
    assert message.template_data == {
        "order_url": "https://example.com/admin/books/order/1/change/",
    }
