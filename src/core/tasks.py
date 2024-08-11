from urllib.parse import urljoin

import requests
from celery import shared_task
from django.urls import reverse
from sentry_sdk.api import capture_exception

from core.conf.environ import env
from core.utils.mailer import Mailer


@shared_task(
    name="core/ping_production_website",
    ignore_result=True,
    autoretry_for=(requests.exceptions.RequestException,),
    retry_backoff=True,
    max_retries=3,
)
def ping_production_website(url=env("PRODUCTION_URL")):
    try:
        response = requests.get(url, headers={"User-Agent": "DjangoLibraryMS/CeleryBeat"})
    except requests.exceptions.RequestException as e:
        capture_exception(e)
        return {"error": str(e)}

    return {
        "url": url,
        "status": response.status_code,
        "response_time": response.elapsed.total_seconds(),
    }


@shared_task(name="core/send_order_created_email")
def send_order_created_email(order_id: int):
    order_path = reverse("admin:books_order_change", kwargs={"object_id": order_id})
    order_url = urljoin(env("PRODUCTION_URL"), order_path)

    body = f"""
        Hi admin! <br />
        Please process new book order <a href='{order_url}' target='_blank'>here</a>
    """
    body_compact = "".join([line.strip() for line in body.split("\n")])
    mailer = Mailer(
        subject="Book order created",
        # to=env("LIBRARIAN_ADMIN_EMAIL"),
        body=body_compact,
    )
    email_sent = mailer.send()

    return {"sent": email_sent}


@shared_task(name="core/send_reservation_confirmed_email")
def send_reservation_confirmed_email(order_id: int):
    from apps.books.models import Order

    reservations_url = urljoin(env("PRODUCTION_URL"), "account/reservations/")

    try:
        order = Order.objects.select_related("book", "member").get(id=order_id)
    except Order.DoesNotExist:
        return {"error": f"Order with id {order_id} does not exist"}

    body = f"""
        Hi {order.member.username}!<br />
        "{order.book.title}" book is ready to be picked up. <br />
        Your Reservation ID: {order.reservation.pk} <br />
        Check all your reservations <a href='{reservations_url}' target='_blank'>here</a>
    """

    mailer = Mailer(
        subject="Book is ready to be picked up",
        # to=(order.member.email,),
        body=body.strip(),
    )
    email_sent = mailer.send()

    order.member_notified = True
    order.save()

    return {"sent": email_sent}
