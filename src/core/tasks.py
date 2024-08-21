from urllib.parse import urljoin

import requests
from celery import shared_task
from django.urls import reverse
from sentry_sdk.api import capture_exception

from apps.users.models import Member
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


@shared_task(name="books/send_order_created_email")
def send_order_created_email(order_id: int):
    order_path = reverse("admin:books_order_change", kwargs={"object_id": order_id})
    order_url = urljoin(env("PRODUCTION_URL"), order_path)

    body = f"""
        Hi admin! <br />
        Please process new book order <a href='{order_url}' target='_blank'>here</a>
    """
    mailer = Mailer(
        subject="Book order created",
        # to=env("LIBRARIAN_ADMIN_EMAIL"),
        body=body,
    )
    email_sent = mailer.send()

    return {"sent": email_sent}


@shared_task(name="books/send_reservation_confirmed_email")
def send_reservation_confirmed_email(order_id: int):
    from apps.books.models import Order

    reservations_url = urljoin(env("PRODUCTION_URL"), "account/reservations/")

    try:
        order = Order.objects.select_related("book", "member").get(id=order_id)
    except Order.DoesNotExist:
        return {"error": f"Order with id {order_id} does not exist"}

    body = f"""
        Hi {order.member.first_name or order.member.username}!<br />
        "{order.book.title}" book is ready to be picked up. <br />
        Your Reservation ID: {order.reservation.pk} <br />
        Check all your reservations <a href='{reservations_url}' target='_blank'>here</a>
    """

    mailer = Mailer(
        subject="Book is ready to be picked up",
        # to=(order.member.email,),
        body=body,
    )
    email_sent = mailer.send()

    order.member_notified = True
    order.save()

    return {"sent": email_sent}


@shared_task(name="core/send_member_registration_request_received")
def send_member_registration_request_received(member_id: int):
    member_admin_path = reverse("admin:users_member_change", kwargs={"object_id": member_id})
    member_admin_url = urljoin(env("PRODUCTION_URL"), member_admin_path)

    body = f"""
        Hi admin! <br />
        New member registration request received. Check <a href='{member_admin_url}' target='_blank'>here</a>
    """
    mailer = Mailer(
        subject="Registration request received",
        # to=env("LIBRARIAN_ADMIN_EMAIL"),
        body=body,
    )
    email_sent = mailer.send()

    return {"sent": email_sent}


@shared_task(name="core/send_registration_notification_to_member")
def send_registration_notification_to_member(member_id: int):
    try:
        member = Member.objects.get(id=member_id)
    except Member.DoesNotExist:
        return {"error": f"Member with id {member_id} does not exist"}

    body = f"""
        Hi {member.first_name or member.username}! <br />
        Your registration code: {member.registration_code}. <br />
        Please arrive to library to complete registration. <br />
        Don't forget to bring your ID card.
    """

    mailer = Mailer(
        subject="Thanks! Your registration request received",
        # to=env("member.email"),
        body=body,
    )

    email_sent = mailer.send()

    return {"sent": email_sent}
