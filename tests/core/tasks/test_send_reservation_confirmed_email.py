import pytest

from core.tasks import send_reservation_confirmed_email

pytestmark = pytest.mark.django_db


def test_send_reservation_confirmed_email_order_does_not_exist():
    order_id = 1

    result = send_reservation_confirmed_email.delay(order_id).get()

    assert result == {"error": f"Order with id {order_id} does not exist"}


def test_send_reservation_confirmed_email_success(mock_mailer, book_order):
    assert not book_order.member_notified

    result = send_reservation_confirmed_email.delay(book_order.id).get()
    book_order.refresh_from_db()

    assert result["sent"] == 1
    assert book_order.member_notified

    mailer_kwargs = mock_mailer.call_args.kwargs
    assert mailer_kwargs["subject"] == "Book is ready to be picked up"
    assert f"Hi {book_order.member.username}!" in mailer_kwargs["body"]
    assert f"{book_order.book.title}" in mailer_kwargs["body"]
    assert "https://example.com/account/reservations/" in mailer_kwargs["body"]


def test_member_not_marked_as_notified_in_case_of_exception(mock_mailer, book_order):
    mock_mailer.return_value.send.side_effect = Exception("Could not send email")

    assert not book_order.member_notified

    with pytest.raises(Exception):
        send_reservation_confirmed_email.delay(book_order.id).get()

    book_order.refresh_from_db()
    assert not book_order.member_notified
