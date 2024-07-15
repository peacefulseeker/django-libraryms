import pytest
from mixer.backend.django import mixer

from apps.books.const import OrderStatus
from apps.books.models import Book, Order

pytestmark = pytest.mark.django_db


def test_order_str_method():
    order = mixer.blend(Order)
    expected_str = f"{order.member.username} - {order.book.title} - {order.status}"
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


# TODO:
def process_next_order_in_queue():
    pass
