from urllib.parse import urljoin

from celery import shared_task
from django.utils import timezone

from apps.books.const import ReservationStatus
from apps.books.models import Reservation
from core.conf.environ import env
from core.utils.mailer import Mailer, Message


@shared_task(name="books/reservation_term_reminder")
def send_reservation_term_reminder(due_in_days=2):
    now = timezone.now()
    reservations: list[Reservation] = Reservation.objects.select_related("book", "member").filter(
        term=now + timezone.timedelta(days=due_in_days), status=ReservationStatus.ISSUED
    )
    messages = []
    reservations_url = urljoin(env("PRODUCTION_URL"), "account/reservations/")
    for reservation in reservations:
        member = reservation.member
        body = f"""
            Hi {member.name}!<br />
            Your book '{reservation.book.title}' reservation is due on {reservation.term}.<br />
            Please return it on time or extend it. <br />
            Otherwise, you will be charged a fine. <br />
            Check all your reservations <a href='{reservations_url}' target='_blank'>here</a>
        """
        messages.append(
            Message(
                subject=f"Reservation term is ending in {due_in_days} days",
                body=body,
            )
        )

    emails_sent = Mailer.send_mass_mail(messages, fail_silently=True)
    return emails_sent
