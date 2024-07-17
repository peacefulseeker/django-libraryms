import pytest
from mixer.backend.django import mixer

from apps.books.models import Book, Order


@pytest.fixture
def book():
    return mixer.blend(Book)


@pytest.fixture
def book_order(member, book):
    return mixer.blend(Order, book=book, member=member)


@pytest.fixture
def create_book_order(member, book):
    def _create_book_order(book=book, member=member, status=None):
        return mixer.blend(Order, book=book, member=member, status=status)

    return _create_book_order


@pytest.fixture
def another_book_order(another_member, book):
    return mixer.blend(Order, book=book, member=another_member)
