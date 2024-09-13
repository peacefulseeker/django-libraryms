import pytest
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mixer.backend.django import mixer
from rest_framework import status as status_codes
from rest_framework.response import Response
from rest_framework.test import APIClient

from apps.books.const import OrderStatus
from apps.books.models.book import Book, Order, Reservation
from apps.users.models import Member

pytestmark = [
    pytest.mark.django_db,
]


class TestBookOrderView:
    @pytest.fixture
    def mock_send_order_created_email(self, mocker):
        return mocker.patch("apps.books.api.views.send_order_created_email")

    @pytest.fixture
    def _setup_max_reservations(self, member):
        for _r in range(Reservation.MAX_RESERVATIONS_PER_MEMBER):
            book = mixer.blend(Book)
            mixer.blend(Order, book=book, member=member, status=OrderStatus.IN_QUEUE)

    def test_max_reservations_reached(self, as_member, _setup_max_reservations):
        extra_book = mixer.blend(Book)

        url = reverse("book-order", kwargs={"book_id": extra_book.id})
        response = as_member.post(url)

        assert response.status_code == status_codes.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == _("Maximum number of reservations reached")

        assert Reservation.objects.count() == Reservation.MAX_RESERVATIONS_PER_MEMBER

    def test_max_queued_orders_reached(self, book_order, authenticated_client: APIClient, another_member):
        book = book_order.book
        url = reverse("book-order", kwargs={"book_id": book.id})

        for _o in range(Order.MAX_QUEUED_ORDERS_ALLOWED):
            member = mixer.blend(Member)
            authenticated_client(member).post(url)

        assert book.enqueued_orders.count() == Order.MAX_QUEUED_ORDERS_ALLOWED

        response = authenticated_client(another_member).post(url)

        assert response.status_code == status_codes.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == _("Maximum number of orders in queue reached")

    def test_auth_needed_to_order_a_book(self, client, book):
        url = reverse("book-order", kwargs={"book_id": book.id})

        response: Response = client.post(url)

        assert response.status_code == status_codes.HTTP_401_UNAUTHORIZED

    def test_order_a_book_new_reservation(self, as_member, book, mock_send_order_created_email):
        url = reverse("book-order", kwargs={"book_id": book.id})

        response: Response = as_member.post(url)

        assert response.status_code == status_codes.HTTP_200_OK
        assert response.data["detail"] == "Book reserved"
        mock_send_order_created_email.delay.assert_called_once_with(response.data["order_id"])

    def test_member_already_has_book_order(self, as_member, book, book_order, mock_send_order_created_email):
        url = reverse("book-order", kwargs={"book_id": book.id})

        response: Response = as_member.post(url)

        assert response.status_code == status_codes.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Book is already ordered or your order is in queue"
        assert book_order.status == OrderStatus.UNPROCESSED
        mock_send_order_created_email.delay.assert_not_called()

    def test_book_order_put_in_queue(self, as_member, book, another_book_order, mock_send_order_created_email):
        url = reverse("book-order", kwargs={"book_id": book.id})

        response: Response = as_member.post(url)

        assert response.status_code == status_codes.HTTP_200_OK
        assert response.data["detail"] == "Book reservation request put in queue"
        assert book.orders.count() == 2
        # first, since sorted by created_at
        assert book.orders.first().id == response.data["order_id"]
        assert book.orders.last() == another_book_order
        mock_send_order_created_email.delay.assert_not_called()

    def test_cancel_book_order(self, as_member, book, book_order):
        url = reverse("book-order", kwargs={"book_id": book.id})

        assert book_order.status == OrderStatus.UNPROCESSED

        response: Response = as_member.delete(url)

        book_order.refresh_from_db()

        assert response.status_code == status_codes.HTTP_204_NO_CONTENT
        assert book_order.status == OrderStatus.MEMBER_CANCELLED

    def test_no_cancellable_order_found(self, as_member, book, another_book_order):
        url = reverse("book-order", kwargs={"book_id": book.id})

        assert another_book_order.status == OrderStatus.UNPROCESSED

        response: Response = as_member.delete(url)

        another_book_order.refresh_from_db()

        assert response.status_code == status_codes.HTTP_404_NOT_FOUND
        assert response.data["detail"] == "No cancellable order found"
        assert another_book_order.status == OrderStatus.UNPROCESSED

    def test_book_order_create_ensure_atomicity(self, as_member, book, mocker):
        url = reverse("book-order", kwargs={"book_id": book.id})
        mocker.patch("apps.books.models.book.Book.save", side_effect=Exception("Could not update book after order reservation created"))

        with pytest.raises(Exception):
            response = as_member.post(url)
            assert response.status_code == status_codes.HTTP_400_BAD_REQUEST

        assert book.orders.count() == 0
        assert book.is_available
        assert Reservation.objects.count() == 0
