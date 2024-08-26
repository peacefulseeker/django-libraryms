from datetime import datetime, timedelta, timezone

import pytest
from mixer.backend.django import mixer

from apps.books.const import ReservationStatus
from apps.books.models import Book, Reservation

frozen_date = datetime(2024, 7, 1, 0, 0, tzinfo=timezone.utc)
pytestmark = pytest.mark.django_db


def test_reservation_str_method():
    reservation = mixer.blend(Reservation)

    expected_str = f"{reservation.pk} - {reservation.member} - {ReservationStatus.RESERVED.label}"
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


def test_reservation_is_completed():
    reservation = mixer.blend(Reservation, status=ReservationStatus.COMPLETED)

    assert reservation.is_completed


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


def test_reservation_ordered_by_modified_at():
    reservation1 = mixer.blend(Reservation)
    reservation2 = mixer.blend(Reservation)
    reservation3 = mixer.blend(Reservation)

    reservation2.save()
    reservation1.save()
    reservation3.save()

    reservations = Reservation.objects.all()

    assert list(reservations) == [reservation3, reservation1, reservation2]


def test_reservation_ordered_by_modified_at_with_nulls_last():
    reservation1 = mixer.blend(Reservation)
    reservation2 = mixer.blend(Reservation)
    reservation3 = mixer.blend(Reservation)

    reservation3.save()
    reservation2.save()

    reservations = Reservation.objects.all()

    assert list(reservations) == [reservation2, reservation3, reservation1]
