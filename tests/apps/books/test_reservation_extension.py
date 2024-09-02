from datetime import date

import pytest
from mixer.backend.django import mixer

from apps.books.const import ReservationExtensionStatus, ReservationStatus
from apps.books.models import ReservationExtension

reservation_term = date(2024, 7, 1)
pytestmark = pytest.mark.django_db


@pytest.fixture
def mock_send_reservation_extension_approved_email(mocker):
    return mocker.patch("apps.books.models.book.send_reservation_extension_approved_email")


@pytest.fixture()
def instance() -> ReservationExtension:
    return mixer.blend(
        ReservationExtension,
        reservation__status=ReservationStatus.ISSUED,
        reservation__term=reservation_term,
    )


def test_defaults(instance):
    assert instance.created_at
    assert not instance.modified_at
    assert instance.reservation.id
    assert instance.reservation_term == reservation_term
    assert instance.reservation.status == ReservationStatus.ISSUED
    assert instance.status == ReservationExtensionStatus.REQUESTED
    assert not instance.processed_by
    assert str(instance) == f"{instance.pk} - {instance.get_status_display()}"


def test_approval(instance, mock_send_reservation_extension_approved_email):
    reservation_term = instance.reservation.term
    instance.status = ReservationExtensionStatus.APPROVED
    instance.save()

    assert instance.modified_at
    assert instance.reservation.term > reservation_term
    assert instance.reservation.extensions_available == instance.reservation.MAX_EXTENSIONS_PER_MEMBER - 1
    mock_send_reservation_extension_approved_email.delay.assert_called_once_with(instance.reservation.id)


def test_extend_once_on_approval(instance):
    instance.status = ReservationExtensionStatus.APPROVED
    instance.save()

    instance.save()
    assert instance.reservation.extensions.count() == 1


def test_reservation_term_extended(instance):
    instance.status = ReservationExtensionStatus.APPROVED
    instance.save()

    assert instance.reservation.term == reservation_term + instance.reservation.RESERVATION_TERM
