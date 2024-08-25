from unittest.mock import call

import pytest
from django.db.utils import IntegrityError
from mixer.backend.django import mixer

from apps.books.const import Language, OrderStatus, ReservationStatus
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


def test_book_ordered_by_last_modified_with_nulls_last():
    book1 = mixer.blend(Book, title="first")
    book2 = mixer.blend(Book, title="second")
    book3 = mixer.blend(Book, title="third")

    book3.save()
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

    assert book.orders.count() == 0

    book.reservation = reservation
    book.save()

    assert book.orders.count() == 1
    assert book.orders.first().status == OrderStatus.PROCESSED


def test_book_available_by_default():
    book: Book = mixer.blend(Book)

    assert book.is_available
    assert book.reservation_id is None
    assert not book.is_booked


def test_not_booked_by_default(book, member):
    book = mixer.blend(Book)

    assert not book.is_booked
    assert not book.is_booked_by_member(member)


def test_book_queued_orders(create_book_order, book):
    create_book_order()
    create_book_order(status=OrderStatus.IN_QUEUE)
    create_book_order(status=OrderStatus.IN_QUEUE)

    queued_orders = book.enqueued_orders

    assert book.has_enqueued_orders
    assert book.orders.count() == 3
    assert len(queued_orders) == 2


def test_book_no_queued_orders(create_book_order, book):
    create_book_order(status=OrderStatus.UNPROCESSED)
    create_book_order(status=OrderStatus.REFUSED)

    queued_orders = book.enqueued_orders

    assert book.orders.count() == 2
    assert len(queued_orders) == 0
    assert not book.has_enqueued_orders


def test_process_next_order_in_queue(create_book_order, book, mock_send_order_created_email):
    create_book_order()
    create_book_order(status=OrderStatus.IN_QUEUE)
    create_book_order(status=OrderStatus.IN_QUEUE)

    assert book.enqueued_orders.count() == 2

    next_order_id_1 = book.enqueued_orders.first().id
    book.process_next_order()

    next_order_id_2 = book.enqueued_orders.first().id
    book.process_next_order()

    assert book.enqueued_orders.count() == 0
    assert all(o.status == OrderStatus.UNPROCESSED for o in book.orders.all())

    # nothing to do
    book.process_next_order()
    assert book.enqueued_orders.count() == 0

    mock_send_order_created_email.delay.has_calls(
        call(next_order_id_1),
        call(next_order_id_2),
    )


def test_book_is_reserved_aka_booked(create_book_order, book, member):
    create_book_order(status=OrderStatus.PROCESSED)

    assert book.is_reserved
    assert book.is_booked
    assert book.reservation_id
    assert not book.reservation_term
    assert book.is_booked_by_member(member)


def test_book_is_issued_aka_booked(book, member):
    order = mixer.blend(Order, book=book, member=member, status=OrderStatus.PROCESSED)
    order.reservation.status = ReservationStatus.ISSUED
    order.reservation.save()

    assert book.is_issued
    assert book.is_booked
    assert book.reservation_id
    assert book.reservation_term
    assert book.is_booked_by_member(member)


def test_book_is_booked_by_another_member(book, another_member, member):
    mixer.blend(Order, book=book, member=another_member, status=OrderStatus.PROCESSED)

    assert book.is_booked
    assert not book.is_booked_by_member(member)
    assert book.is_booked_by_member(another_member)
    assert book.reservation_id
    assert not book.reservation_term
