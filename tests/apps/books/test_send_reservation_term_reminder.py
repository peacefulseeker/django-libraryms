from datetime import datetime, timedelta, timezone

import pytest
from mixer.backend.django import mixer

from apps.books.const import ReservationStatus
from apps.books.models.book import Book, Reservation
from apps.tasks import send_reservation_term_reminder

todays_date = datetime(2024, 8, 31, 0, 0, tzinfo=timezone.utc)
pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time(todays_date.isoformat()),
]


@pytest.fixture(autouse=True)
def mock_send_bulk_templated_email(mocker):
    def mock_send_bulk_templated_email(messages, template):
        return len(messages)

    return mocker.patch("apps.tasks.Mailer.send_bulk_templated_email", side_effect=mock_send_bulk_templated_email)


@pytest.fixture
def _create_book_reservations():
    def create_books_and_reservations(due_in_days: list[int]):
        amount = len(due_in_days)
        books = mixer.cycle(amount).blend(Book)
        for book, due_in_days in zip(books, due_in_days):
            reservation = mixer.blend(Reservation, book=book, status=ReservationStatus.ISSUED, term=todays_date + timedelta(days=due_in_days))
            book.reservation = reservation
            book.save()

    return create_books_and_reservations


def test_no_reminders_sent():
    result = send_reservation_term_reminder.delay().get()

    assert result["sent"] == 0


def test_send_1_reminder_with_default_due_in_days(_create_book_reservations):
    _create_book_reservations(due_in_days=[14, 10, 2])

    assert Reservation.objects.count() == 3
    assert Book.objects.count() == 3

    result = send_reservation_term_reminder.delay().get()

    assert result["sent"] == 1


def test_send_2_reminders(_create_book_reservations):
    _create_book_reservations(due_in_days=[3, 3, 2])

    result = send_reservation_term_reminder.delay(due_in_days=3).get()

    assert result["sent"] == 2


def test_send_bulk_templated_email_args(_create_book_reservations, mock_send_bulk_templated_email):
    _create_book_reservations(due_in_days=[10, 2, 2])

    result = send_reservation_term_reminder.delay(due_in_days=2).get()

    messages = mock_send_bulk_templated_email.call_args[0][0]
    mock_send_bulk_templated_email.call_args[1] == {"template": "MemberReservationReminder"}
    assert result == {"sent": 2, "messages_amount": 2}
    assert mock_send_bulk_templated_email.call_count == 1
    assert messages[0].template_data["reservations_url"] == "https://example.com/account/reservations/"
    assert messages[0].template_data["due_in_days"] == 2
    assert messages[0].template_data["member_name"]
    assert messages[0].template_data["book_title"]
    assert messages[0].template_data["reservation_term"]
