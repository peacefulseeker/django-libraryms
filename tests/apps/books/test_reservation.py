from datetime import date, timedelta

import pytest
from mixer.backend.django import mixer

from apps.books.const import ReservationExtensionStatus, ReservationStatus
from apps.books.models import Book, Reservation
from apps.books.models.book import ReservationExtension

frozen_date = date(2024, 7, 1)
pytestmark = pytest.mark.django_db


def test_reservation_str_method():
    reservation = mixer.blend(Reservation)

    expected_str = f"{reservation.pk} - {reservation.member} - {ReservationStatus.RESERVED.label}"
    assert str(reservation) == expected_str


def test_reservation_defaults_on_create():
    reservation: Reservation = mixer.blend(Reservation)

    assert reservation.status in dict(ReservationStatus.choices).keys()
    assert reservation.status == ReservationStatus.RESERVED
    assert reservation.term is None
    assert not reservation.is_issued
    assert reservation.overdue_days == 0
    assert not reservation.is_overdue
    assert not reservation.is_extendable
    assert reservation.extensions.count() == 0


@pytest.mark.freeze_time(frozen_date.isoformat())
def test_reservation_issued():
    reservation: Reservation = mixer.blend(Reservation, status=ReservationStatus.ISSUED)

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


def test_reservation_ordered_by_created_at():
    reservation1 = mixer.blend(Reservation)
    reservation2 = mixer.blend(Reservation)
    reservation3 = mixer.blend(Reservation)

    reservations = Reservation.objects.all()

    assert list(reservations) == [reservation3, reservation2, reservation1]


def test_reservation_ordered_by_created_at_even_if_modified():
    reservation1 = mixer.blend(Reservation)
    reservation2 = mixer.blend(Reservation)
    reservation3 = mixer.blend(Reservation)

    reservation3.save()
    reservation2.save()
    reservation1.save()

    reservations = Reservation.objects.all()

    assert list(reservations) == [reservation3, reservation2, reservation1]


def test_reservation_is_extendable():
    reservation = mixer.blend(Reservation, status=ReservationStatus.ISSUED)

    assert reservation.is_extendable
    assert reservation.extensions.count() == 0


def test_max_extensions_reached():
    reservation = mixer.blend(Reservation, status=ReservationStatus.ISSUED)
    assert reservation.is_extendable
    term_before_extension = reservation.term

    for _ in range(Reservation.MAX_EXTENSIONS_PER_MEMBER):
        mixer.blend(ReservationExtension, status=ReservationExtensionStatus.APPROVED, reservation=reservation)

    assert not reservation.is_extendable
    assert reservation.extensions.count() == 2
    assert reservation.term > term_before_extension
