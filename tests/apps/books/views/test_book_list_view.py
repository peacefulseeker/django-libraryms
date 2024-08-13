import pytest
from django.conf import settings
from django.urls import reverse
from mixer.backend.django import mixer
from rest_framework import status

from apps.books.api.serializers import BookListSerializer
from apps.books.const import OrderStatus, ReservationStatus
from apps.books.models import Author, Book
from apps.books.models.book import Order, Reservation

pytestmark = pytest.mark.django_db

search_param = settings.REST_FRAMEWORK["SEARCH_PARAM"]


@pytest.fixture(autouse=True)
def _create_books(settings):
    author1 = mixer.blend(Author, first_name="John", last_name="Doe")
    author2 = mixer.blend(Author, first_name="Jane", last_name="Smith")

    mixer.blend(Book, title="Book 1", author=author1)
    mixer.blend(Book, title="Book 2", author=author1)
    mixer.blend(Book, title="Book 3", author=author2)


class TestBookListView:
    url = reverse("books-list")

    def test_list_books(self, client):
        response = client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_search_books_by_title(self, client):
        response = client.get(self.url, {search_param: "Book 1"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["title"] == "Book 1"

    def test_search_books_by_author_first_name(self, client):
        response = client.get(self.url, {search_param: "John"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_search_books_by_author_last_name(self, client):
        response = client.get(self.url, {search_param: "Smith"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["author"]["last_name"] == "Smith"

    def test_get_available_books(self, client):
        response = client.get(self.url, {"available": "true"})
        assert response.status_code == status.HTTP_200_OK

        assert len(response.data) == 3

    def test_get_available_books_reduced(self, client):
        book = Book.objects.first()
        book.reservation = mixer.blend(Reservation)
        book.save(update_fields=["reservation"])

        response = client.get(self.url, {"available": "true"})
        assert response.status_code == status.HTTP_200_OK

        assert len(response.data) == 2

    def test_get_reserved_books_unauthenticated_returns_all(self, client):
        response = client.get(self.url, {"reserved_by_me": "true"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_get_no_reserved_books_as_auth_member(self, as_member):
        response = as_member.get(self.url, {"reserved_by_me": "true"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_reservation_id_is_null_for_visitors(self, client):
        response = client.get(self.url)

        for book in response.data:
            assert book["reservation_id"] is None

    def test_get_a_reserved_book_as_auth_member(self, as_member, member):
        book = Book.objects.first()
        book.reservation = mixer.blend(Reservation, member=member)
        book.save(update_fields=["reservation"])

        response = as_member.get(self.url, {"reserved_by_me": "true"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]["title"] == book.title

    def test_expected_fields_returned(self, as_member):
        expected_fields = BookListSerializer.Meta.fields

        response = as_member.get(self.url)

        assert set(response.data[0]) == set(expected_fields)

    def test_reservation_id_presents_for_reserved_book(self, as_member, member, book):
        order = mixer.blend(Order, book=book, member=member, status=OrderStatus.PROCESSED)
        assert order.reservation.status == ReservationStatus.RESERVED

        response = as_member.get(self.url)

        assert response.data[-1]["reservation_id"] == order.reservation.id

    def test_reservation_id_presents_for_issued_book(self, as_member, member, book):
        order = mixer.blend(Order, book=book, member=member, status=OrderStatus.PROCESSED)
        order.reservation.status == ReservationStatus.ISSUED
        order.reservation.save()

        response = as_member.get(self.url)

        assert response.data[-1]["reservation_id"] == order.reservation.id
