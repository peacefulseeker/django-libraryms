import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from mixer.backend.django import mixer
from rest_framework.status import HTTP_302_FOUND

from apps.books.const import OrderStatus
from apps.books.models import Order
from apps.books.models.book import Book, Reservation

pytestmark = pytest.mark.django_db


@pytest.fixture()
def admin_user():
    User = get_user_model()
    admin_user = User.objects.create_superuser("admin", "admin@example.com", "password")
    return admin_user


@pytest.fixture
def admin_client(client, admin_user):
    client.force_login(admin_user)
    return client


def test_order_save_model(admin_client, book_order, admin_user):
    change_url = reverse("admin:books_order_change", args=[book_order.id])

    assert book_order.status == OrderStatus.UNPROCESSED

    response = admin_client.post(
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


def test_order_delete_model_deletes_associated_reservation(admin_client, book_order):
    delete_url = reverse("admin:books_order_delete", args=[book_order.id])

    assert book_order.reservation is not None
    reservation_id = book_order.reservation.id

    response = admin_client.post(delete_url, {"post": "yes"})  # delete with auto-confirmation

    assert response.status_code == HTTP_302_FOUND  # Expects a redirect after successful deletion
    assert not Order.objects.filter(id=book_order.id).exists()
    assert not Reservation.objects.filter(id=reservation_id).exists()


def test_order_delete_queryset_deletes_associated_reservations(admin_client, member):
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

    response = admin_client.post(changelist_url, data)

    assert response.status_code == HTTP_302_FOUND  # Expects a redirect after successful deletion
    assert not Order.objects.filter(id__in=[order.id for order in orders]).exists()
    assert not Reservation.objects.filter(id__in=reservation_ids).exists()
