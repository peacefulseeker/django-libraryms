import pytest
from mixer.backend.django import mixer

from apps.books.models import Book, Order, Reservation


@pytest.fixture
def book() -> Book:
    return mixer.blend(Book)


@pytest.fixture
def reserved_book(book) -> Book:
    reservation = mixer.blend(Reservation)

    book.reservation = reservation
    book.save()

    return book


@pytest.fixture
def book_order(member, book) -> Order:
    return mixer.blend(Order, book=book, member=member)


@pytest.fixture
def create_book_order(member, book) -> callable:
    def _create_book_order(book=book, member=member, status=None):
        return mixer.blend(Order, book=book, member=member, status=status)

    return _create_book_order


@pytest.fixture
def another_book_order(another_member, book) -> Order:
    return mixer.blend(Order, book=book, member=another_member)
