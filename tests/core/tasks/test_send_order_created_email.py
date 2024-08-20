from core.tasks import send_order_created_email


def test_send_order_created_email(mock_mailer):
    order_id = 1

    result = send_order_created_email.delay(order_id).get()

    assert result["sent"] == 1
    call_kwargs = mock_mailer.call_args.kwargs
    assert call_kwargs["subject"] == "Book order created"
    assert "Hi admin!" in call_kwargs["body"]
    assert "Please process new book order" in call_kwargs["body"]
    assert "https://example.com/admin/books/order/1/change/" in call_kwargs["body"]
