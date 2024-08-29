import pytest

from core.tasks import send_reservation_confirmed_email
from core.utils.mailer import Message

pytestmark = pytest.mark.django_db


def test_send_reservation_confirmed_email_order_does_not_exist():
    order_id = 1
    reservation_id = 1

    result = send_reservation_confirmed_email.delay(order_id, reservation_id).get()

    assert result == {"error": f"Order with id {order_id} does not exist"}


def test_send_reservation_confirmed_email_success(mock_mailer, book_order):
    result = send_reservation_confirmed_email.delay(book_order.id, book_order.reservation.id).get()
    book_order.refresh_from_db()

    assert result["sent"] == 1

    message: Message = mock_mailer.call_args[0][0]
    assert message.subject == "Book is ready to be picked up"
    assert f"Hi {book_order.member.first_name}!" in message.body
    assert f"{book_order.book.title}" in message.body
    assert f"Your Reservation ID: {book_order.reservation.id}" in message.body
    assert "https://example.com/account/reservations/" in message.body


def test_send_reservation_confirmed_email_success_username_used_as_fallback(mock_mailer, book_order):
    book_order.member.first_name = ""
    book_order.member.save()

    send_reservation_confirmed_email.delay(book_order.id, book_order.reservation.id).get()

    message: Message = mock_mailer.call_args[0][0]
    assert f"Hi {book_order.member.username}!" in message.body


def test_member_not_marked_as_notified_in_case_of_exception(mock_mailer, book_order):
    mock_mailer.return_value.send.side_effect = Exception("Could not send email")

    with pytest.raises(Exception):
        send_reservation_confirmed_email.delay(book_order.id, book_order.reservation.id).get()

    book_order.refresh_from_db()
