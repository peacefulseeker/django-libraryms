import pytest
from django.urls import reverse
from mixer.backend.django import mixer
from rest_framework.status import HTTP_302_FOUND

from apps.books.const import OrderStatus
from apps.books.models import Order
from apps.books.models.book import Book, Reservation

pytestmark = pytest.mark.django_db


def test_order_save_model(as_admin, book_order, admin_user):
    change_url = reverse("admin:books_order_change", args=[book_order.id])

    assert book_order.status == OrderStatus.UNPROCESSED

    response = as_admin.post(
        change_url,
        {
            "status": OrderStatus.PROCESSED,
            "change_reason": "Test change reason",
        },
    )

    assert response.status_code == HTTP_302_FOUND  # Expects a redirect after successful save
    book_order.refresh_from_db()
    assert book_order.status == OrderStatus.PROCESSED
    assert book_order.last_modified_by == admin_user
    assert book_order.change_reason == "Test change reason"


def test_order_delete_model_deletes_associated_reservation(as_admin, book_order):
    delete_url = reverse("admin:books_order_delete", args=[book_order.id])

    assert book_order.reservation is not None
    reservation_id = book_order.reservation.id

    response = as_admin.post(delete_url, {"post": "yes"})  # delete with auto-confirmation

    assert response.status_code == HTTP_302_FOUND  # Expects a redirect after successful deletion
    assert not Order.objects.filter(id=book_order.id).exists()
    assert not Reservation.objects.filter(id=reservation_id).exists()


def test_order_delete_queryset_deletes_associated_reservations(as_admin, member):
    books = mixer.cycle(3).blend(Book)
    for book in books:
        mixer.blend(Order, book=book, member=member)
    orders = Order.objects.all()
    reservation_ids = [order.reservation.id for order in orders if order.reservation]

    assert orders.count() == len(reservation_ids)

    changelist_url = reverse("admin:books_order_changelist")
    data = {
        "action": "delete_selected",
        "select_across": 0,
        "index": 0,
        "post": "yes",
        "_selected_action": [order.id for order in orders],
    }

    response = as_admin.post(changelist_url, data)

    assert response.status_code == HTTP_302_FOUND  # Expects a redirect after successful deletion
    assert not Order.objects.filter(id__in=[order.id for order in orders]).exists()
    assert not Reservation.objects.filter(id__in=reservation_ids).exists()
