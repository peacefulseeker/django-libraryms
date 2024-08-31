import pytest
from django.urls import reverse
from rest_framework import status

from apps.books.const import ReservationExtensionStatus

pytestmark = pytest.mark.django_db


class TestReservationExtensionAdmin:
    @pytest.fixture(autouse=True)
    def setup_props(self, reservation_extension):
        self.change_url = reverse("admin:books_reservationextension_change", args=[reservation_extension.id])

    def test_reservation_extension_approve(self, reservation_extension, librarian_staff, as_librarian_staff):
        assert reservation_extension.status == ReservationExtensionStatus.REQUESTED

        response = as_librarian_staff.post(
            self.change_url,
            {
                "status": ReservationExtensionStatus.APPROVED,
            },
        )
        initial_reservation_term = reservation_extension.reservation.term
        assert response.status_code == status.HTTP_302_FOUND
        reservation_extension.refresh_from_db()

        assert reservation_extension.reservation.term > initial_reservation_term
        assert reservation_extension.status == ReservationExtensionStatus.APPROVED
        assert reservation_extension.processed_by == librarian_staff

    def test_reservation_extension_refuse(self, reservation_extension, librarian_staff, as_librarian_staff):
        assert reservation_extension.status == ReservationExtensionStatus.REQUESTED

        response = as_librarian_staff.post(
            self.change_url,
            {
                "status": ReservationExtensionStatus.REFUSED,
            },
        )

        assert response.status_code == status.HTTP_302_FOUND
        reservation_extension.refresh_from_db()
        assert reservation_extension.status == ReservationExtensionStatus.REFUSED
        assert reservation_extension.processed_by == librarian_staff
