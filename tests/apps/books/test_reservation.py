from datetime import datetime, timedelta, timezone

import pytest
from mixer.backend.django import mixer

from apps.books.const import ReservationStatus
from apps.books.models import Book, Reservation

frozen_date = datetime(2024, 7, 1, 0, 0, tzinfo=timezone.utc)
pytestmark = pytest.mark.django_db


def test_reservation_str_method():
    reservation = mixer.blend(Reservation)
    expected_str = f"{reservation.member} - {ReservationStatus.RESERVED.label}"
    assert str(reservation) == expected_str


def test_reservation_defaults_on_create():
    reservation = mixer.blend(Reservation)

    assert reservation.status in dict(ReservationStatus.choices).keys()
    assert reservation.status == ReservationStatus.RESERVED
    assert reservation.term is None
    assert not reservation.is_issued
    assert reservation.overdue_days == 0
    assert not reservation.is_overdue


@pytest.mark.freeze_time(frozen_date.isoformat())
def test_reservation_issued():
    reservation = mixer.blend(Reservation, status=ReservationStatus.ISSUED)

    assert reservation.is_issued
    assert reservation.term == frozen_date + timedelta(days=14)


@pytest.mark.parametrize(("status"), [ReservationStatus.COMPLETED, ReservationStatus.CANCELLED])
def test_reservation_unlinked_from_book_on_status_change(status):
    reservation = mixer.blend(Reservation)
    book = mixer.blend(Book)
    book.reservation = reservation
    book.save()

    reservation.status = status
    reservation.save()

    assert book.reservation is None
    assert not hasattr(reservation, "book")


def test_reservation_ordering():
    reservation1 = mixer.blend(Reservation)
    reservation2 = mixer.blend(Reservation)
    reservation3 = mixer.blend(Reservation)

    reservations = Reservation.objects.all()

    assert list(reservations) == [reservation3, reservation2, reservation1]
