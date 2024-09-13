import pytest
from django.urls import reverse
from mixer.backend.django import mixer
from rest_framework import status
from rest_framework.response import Response

from apps.books.const import ReservationExtensionStatus
from apps.books.models.book import Reservation, ReservationExtension

pytestmark = pytest.mark.django_db


class TestReservationExtendView:
    @pytest.fixture(autouse=True)
    def setup_props(self, book):
        self.url = reverse("book-reservation-extend", kwargs={"book_id": book.id})

    @pytest.fixture
    def _setup_max_reservation_extensions(self, member_reservation):
        for _r in range(Reservation.MAX_EXTENSIONS_PER_MEMBER):
            mixer.blend(ReservationExtension, reservation=member_reservation, status=ReservationExtensionStatus.APPROVED)

    def test_auth_required(self, client):
        response: Response = client.post(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_reservation_requested(self, as_member, member_reservation: Reservation):
        current_term = member_reservation.term

        response: Response = as_member.post(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Reservation extension requested"

        assert member_reservation.extensions.count() == 1
        assert member_reservation.extensions.first().status == ReservationExtensionStatus.REQUESTED
        assert member_reservation.term == current_term

    def test_reservation_not_found(self, as_another_member, member_reservation: Reservation):
        response: Response = as_another_member.post(self.url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["detail"] == "No reservation found"

        assert member_reservation.extensions.count() == 0

    def test_pending_extension_exists(self, as_member, member_reservation: Reservation):
        as_member.post(self.url)
        assert member_reservation.extensions.count() == 1

        response: Response = as_member.post(self.url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Reservation extension already requested"

    def test_max_reservation_extensions_reached(self, _setup_max_reservation_extensions, as_member, member_reservation: Reservation):
        assert member_reservation.extensions.count() == Reservation.MAX_EXTENSIONS_PER_MEMBER

        response: Response = as_member.post(self.url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Reservation cannot be extended"


class TestReservationExtendCancelView:
    @pytest.fixture(autouse=True)
    def setup_props(self, book):
        self.url = reverse("book-reservation-extend", kwargs={"book_id": book.id})

    def test_auth_required(self, client):
        response: Response = client.delete(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_reservation_not_found(self, as_another_member, member_reservation):
        response: Response = as_another_member.delete(self.url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["detail"] == "No reservation found"

    def test_no_requested_extension_exists(self, as_member, member_reservation):
        response: Response = as_member.delete(self.url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "No cancellable reservation extension found"

    def test_cancel_requested_extension(self, as_member, reservation_extension):
        assert reservation_extension.status == ReservationExtensionStatus.REQUESTED
        response = as_member.delete(self.url)

        assert response.status_code == status.HTTP_200_OK
        reservation_extension.refresh_from_db()
        assert reservation_extension.status == ReservationExtensionStatus.CANCELLED

    def test_cancel_requested_extension_with_1_extension_left_hint(self, as_member, reservation_extension, mocker):
        mocker.patch("apps.books.models.book.Reservation.extensions_available", return_value=1, new_callable=mocker.PropertyMock)

        assert reservation_extension.status == ReservationExtensionStatus.REQUESTED
        response = as_member.delete(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "You have 1 more extension available for this book"

    def test_cancel_requested_extension_with_4_extensions_left_hint(self, as_member, reservation_extension, mocker):
        mocker.patch("apps.books.models.book.Reservation.extensions_available", return_value=4, new_callable=mocker.PropertyMock)

        assert reservation_extension.status == ReservationExtensionStatus.REQUESTED
        response = as_member.delete(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "You have 4 more extensions available for this book"

    def test_cancel_requested_extension_with_no_more_extensions_left_hint(self, as_member, reservation_extension, mocker):
        mocker.patch("apps.books.models.book.Reservation.extensions_available", return_value=0, new_callable=mocker.PropertyMock)

        assert reservation_extension.status == ReservationExtensionStatus.REQUESTED
        response = as_member.delete(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "You have no more extensions available for this book"

    def test_cant_cancel_approved_extension(self, as_member, reservation_extension):
        reservation_extension.status = ReservationExtensionStatus.APPROVED
        reservation_extension.save()

        response = as_member.delete(self.url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "No cancellable reservation extension found"
