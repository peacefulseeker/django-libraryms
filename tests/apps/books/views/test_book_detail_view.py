import pytest
from django.urls import reverse
from mixer.backend.django import mixer
from rest_framework import status

from apps.books.api.serializers import BookSerializer
from apps.books.const import OrderStatus, ReservationStatus
from apps.books.models import Book, Reservation
from apps.books.models.book import Order

pytestmark = pytest.mark.django_db


def test_retrieves_existing_book(client):
    book = mixer.blend(Book)
    url = reverse("book-detail", kwargs={"pk": book.id})

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == book.id
    assert response.data["title"] == book.title


def test_returns_404_for_nonexistent_book(client):
    non_existent_id = 9999
    url = reverse("book-detail", kwargs={"pk": non_existent_id})

    response = client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_expected_fields_returned(client):
    book = mixer.blend(Book)
    url = reverse("book-detail", kwargs={"pk": book.id})

    response = client.get(url)

    expected_fields = BookSerializer.Meta.fields

    assert set(response.data) == set(expected_fields)


def test_auth_related_fields_falsy_for_visitors(client, book):
    url = reverse("book-detail", kwargs={"pk": book.id})
    response = client.get(url)

    assert not any(
        [
            response.data["is_issued_to_member"],
            response.data["is_reserved_by_member"],
            response.data["is_queued_by_member"],
            response.data["max_reservations_reached"],
        ]
    )


def test_with_related_objects(client):
    book = mixer.blend(Book, author__first_name="Test Author", publisher__name="Test Publisher")
    url = reverse("book-detail", kwargs={"pk": book.id})

    response = client.get(url)

    assert response.data["author"]["first_name"] == "Test Author"
    assert response.data["publisher"]["name"] == "Test Publisher"


def test_handles_unicode_characters(client):
    book = mixer.blend(Book, title="Книга на русском")
    url = reverse("book-detail", kwargs={"pk": book.id})

    response = client.get(url)

    assert response.data["title"] == "Книга на русском"


def test_is_not_issued_to_member(as_member, book, member):
    order = mixer.blend(Order, book=book, member=member, status=OrderStatus.PROCESSED)
    assert order.reservation.status != ReservationStatus.ISSUED

    url = reverse("book-detail", kwargs={"pk": book.id})
    response = as_member.get(url)

    assert not response.data["is_issued_to_member"]


def test_is_issued_to_member(as_member, book, member):
    order = mixer.blend(Order, book=book, member=member, status=OrderStatus.PROCESSED)
    order.reservation.status = ReservationStatus.ISSUED
    order.reservation.save()

    url = reverse("book-detail", kwargs={"pk": book.id})
    response = as_member.get(url)

    assert response.data["is_issued_to_member"]


def test_is_reserved_by_member(as_member, book, member):
    order = mixer.blend(Order, book=book, member=member, status=OrderStatus.PROCESSED)
    assert order.reservation.status == ReservationStatus.RESERVED

    url = reverse("book-detail", kwargs={"pk": book.id})
    response = as_member.get(url)

    assert response.data["is_reserved_by_member"]


def test_is_not_reserved_by_member(as_member, book):
    url = reverse("book-detail", kwargs={"pk": book.id})

    response = as_member.get(url)

    assert not response.data["is_reserved_by_member"]


def test_is_queued_by_member(as_member, book, member):
    mixer.blend(Order, book=book, member=member, status=OrderStatus.IN_QUEUE)
    url = reverse("book-detail", kwargs={"pk": book.id})

    response = as_member.get(url)

    assert response.data["is_queued_by_member"]


def test_is_not_queued_by_member(as_member, book):
    url = reverse("book-detail", kwargs={"pk": book.id})

    response = as_member.get(url)

    assert not response.data["is_queued_by_member"]


def test_max_reservations_reached_not_reached_yet(as_member, book, member):
    mixer.cycle(Reservation.MAX_RESERVATIONS_PER_MEMBER - 1).blend(Order, member=member)

    url = reverse("book-detail", kwargs={"pk": book.id})
    response = as_member.get(url)

    assert not response.data["max_reservations_reached"]


def test_max_reservations_reached(as_member, book, member):
    mixer.cycle(Reservation.MAX_RESERVATIONS_PER_MEMBER).blend(Order, member=member)

    url = reverse("book-detail", kwargs={"pk": book.id})
    response = as_member.get(url)

    assert response.data["max_reservations_reached"]
