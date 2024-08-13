import pytest
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
)

from apps.books.const import OrderStatus

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def mock_send_order_created_email(mocker):
    return mocker.patch("apps.books.api.views.send_order_created_email")


def test_no_auth_needed_to_view_books_list(client):
    url = reverse("books-list")

    response: Response = client.get(url)

    assert response.status_code == HTTP_200_OK


def test_no_auth_needed_to_view_a_single_book(client, book):
    url = reverse("book-detail", kwargs={"pk": book.id})

    response: Response = client.get(url)

    assert response.status_code == HTTP_200_OK


def test_auth_needed_to_order_a_book(client, book):
    url = reverse("book-order", kwargs={"book_id": book.id})

    response: Response = client.post(url)

    assert response.status_code == HTTP_401_UNAUTHORIZED


def test_order_a_book_new_reservation(as_member, book, mock_send_order_created_email):
    url = reverse("book-order", kwargs={"book_id": book.id})

    response: Response = as_member.post(url)

    assert response.status_code == HTTP_200_OK
    assert response.data["detail"] == "Book reserved"
    mock_send_order_created_email.delay.assert_called_once_with(response.data["order_id"])


def test_member_already_has_book_order(as_member, book, book_order, mock_send_order_created_email):
    url = reverse("book-order", kwargs={"book_id": book.id})

    response: Response = as_member.post(url)

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.data["detail"] == "Book is already ordered or your order is in queue"
    assert book_order.status == OrderStatus.UNPROCESSED
    mock_send_order_created_email.delay.assert_not_called()


def test_book_order_put_in_queue(as_member, book, another_book_order, mock_send_order_created_email):
    url = reverse("book-order", kwargs={"book_id": book.id})

    response: Response = as_member.post(url)

    assert response.status_code == HTTP_200_OK
    assert response.data["detail"] == "Book reservation request put in queue"
    assert book.orders.count() == 2
    # first, since sorted by created_at
    assert book.orders.first().id == response.data["order_id"]
    assert book.orders.last() == another_book_order
    mock_send_order_created_email.delay.assert_not_called()


def test_cancel_book_order(as_member, book, book_order):
    url = reverse("book-order", kwargs={"book_id": book.id})

    assert book_order.status == OrderStatus.UNPROCESSED

    response: Response = as_member.delete(url)

    book_order.refresh_from_db()

    assert response.status_code == HTTP_204_NO_CONTENT
    assert book_order.status == OrderStatus.MEMBER_CANCELLED


def test_no_cancellable_order_found(as_member, book, another_book_order):
    url = reverse("book-order", kwargs={"book_id": book.id})

    assert another_book_order.status == OrderStatus.UNPROCESSED

    response: Response = as_member.delete(url)

    another_book_order.refresh_from_db()

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.data["detail"] == "No cancellable order found"
    assert another_book_order.status == OrderStatus.UNPROCESSED
