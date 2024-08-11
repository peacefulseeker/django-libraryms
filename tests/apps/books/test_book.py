from unittest.mock import call

import pytest
from django.db.utils import IntegrityError
from mixer.backend.django import mixer

from apps.books.const import Language, OrderStatus
from apps.books.models import Author, Book, Order, Publisher, Reservation

pytestmark = pytest.mark.django_db


@pytest.fixture
def mock_send_order_created_email(mocker):
    return mocker.patch("apps.books.models.book.send_order_created_email")


def test_book_str_method():
    book = mixer.blend(Book, title="Test Title")
    assert str(book) == "Test Title"


def test_book_title_max_length():
    book = mixer.blend(Book)
    max_length = book._meta.get_field("title").max_length
    assert max_length == 200


def test_book_title_uniqueness():
    book1 = mixer.blend(Book)
    with pytest.raises(IntegrityError):
        mixer.blend(Book, title=book1.title)


def test_book_author_relation():
    author = mixer.blend(Author)
    book = mixer.blend(Book, author=author)
    assert book.author == author


def test_books_order_by_modified_at_first():
    book1 = mixer.blend(Book, title="first")
    book2 = mixer.blend(Book, title="second")
    book3 = mixer.blend(Book, title="third")

    book1.title += " (Updated)"
    book1.save()

    book3.title += " (Updated)"
    book3.save()

    book2.title += " (Updated)"
    book2.save()

    books = Book.objects.all()
    assert list(books) == [book2, book3, book1]


def test_book_publisher_relation():
    publisher = mixer.blend(Publisher)
    book = mixer.blend(Book, publisher=publisher)
    assert book.publisher == publisher


def test_book_language_choices():
    book = mixer.blend(Book)
    assert book.language in dict(Language.choices).keys()


def test_book_published_at_positive():
    book = mixer.blend(Book)
    assert book.published_at > 0


def test_book_pages_positive():
    book = mixer.blend(Book)
    assert book.pages > 0


def test_book_isbn_max_length():
    book = mixer.blend(Book)
    max_length = book._meta.get_field("isbn").max_length
    assert max_length == 13


def test_book_reservation_relation():
    reservation = mixer.blend(Reservation)
    book = mixer.blend(Book)
    book.reservation = reservation
    book.save()
    assert book.reservation == reservation


def test_processed_order_created_when_reservation_assigned():
    reservation = mixer.blend(Reservation)
    book = mixer.blend(Book)

    assert book.order_set.count() == 0

    book.reservation = reservation
    book.save()

    assert book.order_set.count() == 1
    assert book.order_set.first().status == OrderStatus.PROCESSED


def test_book_available_by_default():
    book = mixer.blend(Book)
    assert book.reservation is None
    assert book.is_available


def test_book_queued_orders():
    book: Book = mixer.blend(Book)
    order1 = mixer.blend(Order, book=book, status=OrderStatus.IN_QUEUE)
    order2 = mixer.blend(Order, book=book, status=OrderStatus.IN_QUEUE)
    order3 = mixer.blend(Order, book=book, status=OrderStatus.PROCESSED)

    queued_orders = book.queued_orders

    assert book.has_orders_in_queue
    assert book.order_set.count() == 3
    assert len(queued_orders) == 2
    assert order1 in queued_orders
    assert order2 in queued_orders
    assert order3 not in queued_orders


def test_book_no_queued_orders():
    book: Book = mixer.blend(Book)
    mixer.blend(Order, book=book, status=OrderStatus.PROCESSED)
    mixer.blend(Order, book=book, status=OrderStatus.REFUSED)

    queued_orders = book.queued_orders

    assert book.order_set.count() == 2
    assert len(queued_orders) == 0
    assert not book.has_orders_in_queue


def test_unqueue_next_order_in_queue(create_book_order, member, book, mock_send_order_created_email):
    create_book_order(status=OrderStatus.UNPROCESSED)
    create_book_order(status=OrderStatus.IN_QUEUE)
    create_book_order(status=OrderStatus.IN_QUEUE)

    assert book.queued_orders.count() == 2

    next_order_id_1 = book.queued_orders.first().id
    book.unqueue_next_order()

    next_order_id_2 = book.queued_orders.first().id
    book.unqueue_next_order()

    assert book.queued_orders.count() == 0
    assert all(o.status == OrderStatus.UNPROCESSED for o in book.order_set.all())

    # nothing to do
    book.unqueue_next_order()
    assert book.queued_orders.count() == 0

    mock_send_order_created_email.delay.has_calls(
        call(next_order_id_1),
        call(next_order_id_2),
    )
