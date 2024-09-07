import pytest

from apps.users.models import Member
from core.tasks import send_reservation_extension_approved_email
from core.utils.mailer import Message

pytestmark = pytest.mark.django_db


def test_reservation_does_not_exist():
    reservation_id = 1

    result = send_reservation_extension_approved_email.delay(reservation_id).get()

    assert result["error"] == f"Reservation with id {reservation_id} does not exist"


def test_success(mock_mailer, member_reservation):
    result = send_reservation_extension_approved_email.delay(member_reservation.id).get()
    member: Member = member_reservation.member

    assert result["sent"]
    message: Message = mock_mailer.send_templated_email.call_args[0][0]
    assert message.template_name == "MemberReservationExtensionApproved"
    assert message.template_data == {
        "member_name": member.name,
        "book_title": member_reservation.book.title,
        "reservation_term": str(member_reservation.term),
        "reservations_url": "https://example.com/account/reservations/",
    }
