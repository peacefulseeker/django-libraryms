import pytest
from mixer.backend.django import mixer

from apps.books.const import ReservationStatus
from apps.books.models import Book, Order
from apps.books.models.book import Reservation, ReservationExtension


@pytest.fixture
def book() -> Book:
    return mixer.blend(Book)


@pytest.fixture
def book_order(member, book) -> Order:
    return mixer.blend(Order, book=book, member=member)


@pytest.fixture
def another_book_order(another_member, book) -> Order:
    return mixer.blend(Order, book=book, member=another_member)


@pytest.fixture
def create_book_order(member, book) -> callable:
    def _create_book_order(book=book, member=member, status=Order.status.field.default):
        return mixer.blend(Order, book=book, member=member, status=status)

    return _create_book_order


@pytest.fixture
def member_reservation(book, member) -> Reservation:
    issued_reservation = mixer.blend(Reservation, status=ReservationStatus.ISSUED, book=book, member=member)
    book.reservation = issued_reservation
    book.save()
    return issued_reservation


@pytest.fixture
def reservation_extension(member_reservation) -> ReservationExtension:
    return mixer.blend(ReservationExtension, reservation=member_reservation)
