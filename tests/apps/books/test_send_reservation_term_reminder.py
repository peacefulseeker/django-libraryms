from datetime import datetime, timedelta, timezone

import pytest
from mixer.backend.django import mixer

from apps.books.const import ReservationStatus
from apps.books.models.book import Book, Reservation
from apps.tasks import send_reservation_term_reminder
from core.utils.mailer import Message

todays_date = datetime(2024, 8, 31, 0, 0, tzinfo=timezone.utc)
pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time(todays_date.isoformat()),
]


def errored_ses_message_headers():
    return {
        "message": "Message",
        "reason": "No clue",
        "status": 500,
        "error_message": "Failed to send email",
        "error_code": 123,
    }


@pytest.fixture
def mock_send_mass_mail(mocker):
    return mocker.patch("apps.tasks.Mailer.send_mass_mail")


@pytest.fixture
def _mock_send_messages_with_failure(mocker):
    def mock_send_messages_with_failure(failed_indices: list[int]):
        def mock_send_messages(messages: list[Message]):
            for i in failed_indices:
                messages[i].extra_headers = errored_ses_message_headers()

            return len(messages) - len(failed_indices)

        get_connection_mock = mocker.patch("core.utils.mailer.get_connection")
        get_connection_mock.return_value.send_messages.side_effect = mock_send_messages
        return get_connection_mock

    return mock_send_messages_with_failure


@pytest.fixture
def mock_sentry_capture_message(mocker):
    return mocker.patch("core.utils.mailer.sentry_sdk.capture_message")


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


def test_individual_message_properties(_create_book_reservations, mock_send_mass_mail):
    _create_book_reservations(due_in_days=[10, 2, 2])

    send_reservation_term_reminder.delay(due_in_days=2)

    messages = mock_send_mass_mail.call_args[0][0]
    fail_silently = mock_send_mass_mail.call_args[1]["fail_silently"]
    assert fail_silently
    assert mock_send_mass_mail.call_count == 1
    assert len(messages) == 2
    assert messages[0].subject == messages[1].subject == "Reservation term is ending in 2 days"
    assert messages[0].body != messages[1].body
    assert "https://example.com/account/reservations/" in messages[0].body


def test_single_failed_delivery_captured(_create_book_reservations, mock_sentry_capture_message, _mock_send_messages_with_failure):
    _create_book_reservations(due_in_days=[10, 2, 2])
    fail_first_index = 0
    mocked_sent = _mock_send_messages_with_failure(failed_indices=[fail_first_index])

    result = send_reservation_term_reminder.delay(due_in_days=2).get()

    assert result == {"sent": 1}
    messages = mocked_sent.return_value.send_messages.call_args[0][0]
    assert len(messages) == 2
    assert messages[fail_first_index].extra_headers == errored_ses_message_headers()

    assert mock_sentry_capture_message.call_count == 1
    sentry_message = mock_sentry_capture_message.call_args[0][0]
    sentry_extra = mock_sentry_capture_message.call_args[1]
    assert sentry_message == "Failed to send reminder email"
    assert sentry_extra["extra"] == messages[fail_first_index].extra_headers


def test_multiple_failed_deliveries_captured(_create_book_reservations, mock_sentry_capture_message, _mock_send_messages_with_failure):
    _create_book_reservations(due_in_days=[10, 2, 2, 2, 2])
    mocked_sent = _mock_send_messages_with_failure(failed_indices=[0, 1])

    result = send_reservation_term_reminder.delay(due_in_days=2).get()

    assert result == {"sent": 2}
    messages = mocked_sent.return_value.send_messages.call_args[0][0]
    assert len(messages) == 4

    assert mock_sentry_capture_message.call_count == 2
