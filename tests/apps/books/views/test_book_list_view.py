import pytest
from django.conf import settings
from django.urls import reverse
from mixer.backend.django import mixer
from rest_framework import status

from apps.books.api.serializers import BookEnqueuedByMemberSerializer, BookListSerializer, BooksReservedByMemberSerializer
from apps.books.const import OrderStatus, ReservationStatus
from apps.books.models import Author, Book
from apps.books.models.book import Order, Reservation
from apps.users.models import Member

pytestmark = pytest.mark.django_db


@pytest.fixture()
def create_books(request):
    if "skip_create_books" in request.keywords:
        return

    author1 = mixer.blend(Author, first_name="John", last_name="Doe")
    author2 = mixer.blend(Author, first_name="Jane", last_name="Smith")

    mixer.blend(Book, title="Book 1", author=author1)
    mixer.blend(Book, title="Book 2", author=author1)
    mixer.blend(Book, title="Book 3", author=author2)


@pytest.mark.usefixtures("create_books")
class TestBookListView:
    url = reverse("books-list")
    search_param = settings.REST_FRAMEWORK["SEARCH_PARAM"]
    expected_fields = BookListSerializer.Meta.fields

    def test_list_books(self, client):
        response = client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_search_books_by_title(self, client):
        response = client.get(self.url, {self.search_param: "Book 1"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["title"] == "Book 1"

    def test_search_books_by_author_first_name(self, client):
        response = client.get(self.url, {self.search_param: "John"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_search_books_by_author_last_name(self, client):
        response = client.get(self.url, {self.search_param: "Smith"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["author"]["last_name"] == "Smith"

    def test_get_available_books(self, client):
        response = client.get(self.url, {"available": ""})
        assert response.status_code == status.HTTP_200_OK

        assert len(response.data) == 3

    def test_get_available_books_reduced(self, client):
        book = Book.objects.first()
        book.reservation = mixer.blend(Reservation)
        book.save(update_fields=["reservation"])

        response = client.get(self.url, {"available": ""})
        assert response.status_code == status.HTTP_200_OK

        assert len(response.data) == 2

    def test_expected_list_fields_returned_as_member(self, as_member):
        response = as_member.get(self.url)

        assert set(response.data[0]) == set(self.expected_fields)

    def test_expected_list_fields_returned_as_visitor(self, client):
        response = client.get(self.url)

        assert set(response.data[0]) == set(self.expected_fields)


@pytest.mark.usefixtures("create_books")
class TestBooksReservedByMemberView:
    url = reverse("books-list")
    expected_reserved_fields = BooksReservedByMemberSerializer.Meta.fields
    expected_enqueued_fields = BookEnqueuedByMemberSerializer.Meta.fields

    @pytest.fixture
    def _create_book_orders(self, authenticated_client):
        def _create(n=2):
            book = mixer.blend(Book)
            url = reverse("book-order", kwargs={"book_id": book.id})

            for _ in range(n):
                _member = mixer.blend(Member)
                authenticated_client(_member).post(url)

            return book, url

        return _create

    def test_get_reserved_books_unauthenticated_returns_all(self, client):
        response = client.get(self.url, {"reserved_by_me": ""})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_get_no_reserved_books_as_auth_member(self, as_member):
        response = as_member.get(self.url, {"reserved_by_me": ""})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_fields_not_expected_for_visitors(self, client):
        response = client.get(self.url, {"reserved_by_me": ""})

        for book in response.data:
            assert "reservation_id" not in book
            assert "reservation_term" not in book
            assert "is_issued" not in book
            assert "is_enqueued_by_member" not in book
            assert "amount_in_queue" not in book

    def test_get_a_reserved_book_as_auth_member(self, as_member, member):
        book = Book.objects.first()
        book.reservation = mixer.blend(Reservation, member=member)
        book.save(update_fields=["reservation"])

        response = as_member.get(self.url, {"reserved_by_me": ""})

        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]["title"] == book.title

    @pytest.mark.skip_create_books
    def test_reservation_id_presents_for_a_reserved_book(self, as_member, member, book):
        order = mixer.blend(Order, book=book, member=member, status=OrderStatus.PROCESSED)
        assert order.reservation.status == ReservationStatus.RESERVED

        response = as_member.get(self.url, {"reserved_by_me": ""})

        # assuming most recently added books are placed first
        assert response.data[0]["reservation_id"] == order.reservation.id
        assert response.data[0]["title"] == book.title

    @pytest.mark.skip_create_books
    def test_reservation_id_presents_for_an_issued_book(self, as_member, member, book):
        order = mixer.blend(Order, book=book, member=member, status=OrderStatus.PROCESSED)
        order.reservation.status = ReservationStatus.ISSUED
        order.reservation.save()

        response = as_member.get(self.url, {"reserved_by_me": ""})

        # assuming most recently added books are placed first
        assert set(response.data[0]) == set(self.expected_reserved_fields)
        assert response.data[0]["reservation_id"] == order.reservation.id
        assert response.data[0]["title"] == book.title

    def test_list_contains_single_enqueued_book_of_member(self, _create_book_orders, authenticated_client, member):
        book, url = _create_book_orders(n=1)

        enqueued_order_placed = authenticated_client(member).post(url)
        assert enqueued_order_placed.data["book_id"] == book.id

        assert book.orders.count() == 2

        response = authenticated_client(member).get(self.url, {"enqueued_by_me": ""})
        assert len(response.data) == 1
        enqueued_book = response.data[0]
        assert enqueued_book["amount_in_queue"] == 1
        assert set(enqueued_book) == set(self.expected_enqueued_fields)

    def test_list_contains_reserved_and_enqueued_book_of_member(self, book_order, _create_book_orders, authenticated_client, member):
        book, url = _create_book_orders(n=2)

        enqueued_order_placed = authenticated_client(member).post(url)
        assert enqueued_order_placed.data["book_id"] == book.id

        assert book.orders.count() == 3

        response = authenticated_client(member).get(self.url, {"reserved_by_me": ""})

        assert len(response.data) == 1
        reserved_book = response.data[0]
        assert reserved_book["id"] == book_order.book.id
        assert reserved_book["reservation_id"] == book_order.reservation.id
        assert reserved_book["reservation_term"] == book_order.reservation.term

        response = authenticated_client(member).get(self.url, {"enqueued_by_me": ""})

        assert len(response.data) == 1
        enqueued_book = response.data[0]
        assert enqueued_book["id"] == book.id
        assert enqueued_book["amount_in_queue"] == 2

        assert set(enqueued_book) == set(self.expected_enqueued_fields)
        assert set(reserved_book) == set(self.expected_reserved_fields)
