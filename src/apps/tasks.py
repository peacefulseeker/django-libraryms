from urllib.parse import urljoin

from celery import shared_task
from django.utils import timezone

from apps.books.const import ReservationStatus
from apps.books.models import Reservation
from core.conf.environ import env
from core.utils.mailer import Mailer, Message


@shared_task(name="books/reservation_term_reminder")
def send_reservation_term_reminder(due_in_days: int = 2) -> dict[str, int]:
    now = timezone.now()
    reservations: list[Reservation] = Reservation.objects.select_related("book", "member").filter(
        term=now + timezone.timedelta(days=due_in_days), status=ReservationStatus.ISSUED
    )
    messages = []
    reservations_url = urljoin(env("PRODUCTION_URL"), "account/reservations/")
    for reservation in reservations:
        message: Message = Message(
            template_data={
                "due_in_days": due_in_days,
                "member_name": reservation.member.name,
                "book_title": reservation.book.title,
                "reservation_term": str(reservation.term),
                "reservations_url": reservations_url,
            },
            template_name="MemberReservationReminder",
        )
        messages.append(message)
    emails_sent = Mailer.send_bulk_templated_email(
        messages,
        template="MemberReservationReminder",
    )
    return {
        "sent": emails_sent,
        "messages_amount": len(messages),
    }
