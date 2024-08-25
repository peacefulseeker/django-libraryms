import pytest
from mixer.backend.django import mixer

from apps.books.const import OrderStatus, ReservationStatus
from apps.books.models import Book, Order, Reservation

pytestmark = pytest.mark.django_db


@pytest.fixture
def mock_send_reservation_confirmed_email(mocker):
    return mocker.patch("apps.books.models.book.send_reservation_confirmed_email")


def test_order_str_method():
    order = mixer.blend(Order)
    expected_str = f"{order.member} - {order.book} - {order.status}"
    assert str(order) == expected_str


def test_order_default_status():
    order = mixer.blend(Order)
    assert order.status in dict(OrderStatus.choices).keys()
    assert order.status == OrderStatus.UNPROCESSED


def test_orders_sorted_by_created_at():
    order1 = mixer.blend(Order)
    order2 = mixer.blend(Order)
    order3 = mixer.blend(Order)

    orders = Order.objects.all()
    assert list(orders) == [order3, order2, order1]


def test_reservation_created_on_save():
    book: Book = mixer.blend(Book)
    mixer.blend(Order, book=book)

    assert not book.is_available
    assert book.reservation.book.id == book.id


def test_orders_processable(create_book_order, book, member, another_member):
    create_book_order(status=OrderStatus.PROCESSED)
    create_book_order(status=OrderStatus.IN_QUEUE)
    create_book_order(status=OrderStatus.UNPROCESSED)
    create_book_order(status=OrderStatus.MEMBER_CANCELLED)
    create_book_order(status=OrderStatus.REFUSED)

    create_book_order(member=another_member, status=OrderStatus.MEMBER_CANCELLED)
    create_book_order(member=another_member, status=OrderStatus.REFUSED)

    assert Order.objects.processable(book.id, member.id).count() == 2
    assert Order.objects.processable(book.id, another_member.id).count() == 0


def test_cancel_order(create_book_order):
    order = create_book_order(status=OrderStatus.IN_QUEUE)

    assert order.status == OrderStatus.IN_QUEUE
    order.cancel()

    assert order.status == OrderStatus.MEMBER_CANCELLED


def test_reservation_deleted_through_order(create_book_order):
    order: Order = create_book_order(status=OrderStatus.UNPROCESSED)

    assert Reservation.objects.reserved_by_member(order.member_id).count() == 1

    order.delete_reservation()

    assert Reservation.objects.reserved_by_member(order.member_id).count() == 0


def test_reservation_confirmation(create_book_order, mock_send_reservation_confirmed_email):
    order = create_book_order(status=OrderStatus.UNPROCESSED)

    mock_send_reservation_confirmed_email.delay.assert_not_called()

    order.status = OrderStatus.PROCESSED
    order.save()

    mock_send_reservation_confirmed_email.delay.assert_called_once_with(order.pk, order.reservation.pk)
    order.refresh_from_db()


def test_refused_order_refuses_reservation(book_order):
    assert book_order.reservation.status == ReservationStatus.RESERVED

    book_order.status = OrderStatus.REFUSED
    book_order.save()

    assert book_order.reservation.status == ReservationStatus.REFUSED
