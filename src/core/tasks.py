from urllib.parse import urljoin

import requests
from celery import Task as BaseTask
from celery import shared_task
from celery_singleton import Singleton
from django.db import transaction
from django.urls import reverse
from sentry_sdk.api import capture_exception

from apps.users.models import Member
from core.conf.environ import env
from core.utils.mailer import Mailer, Message

SingletonOrTask = Singleton if not env.bool("CELERY_ALWAYS_EAGER", default=False) else BaseTask


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
        Message(
            subject="Book order created",
            # to=env("LIBRARIAN_ADMIN_EMAIL"),
            body=body,
        )
    )
    email_sent = mailer.send()

    return {"sent": email_sent}


@shared_task(name="books/send_reservation_confirmed_email", base=SingletonOrTask, unique_on=["reservation_id"])
def send_reservation_confirmed_email(order_id: int, reservation_id: int):
    from apps.books.models import Order

    reservations_url = urljoin(env("PRODUCTION_URL"), "account/reservations/")

    try:
        order = Order.objects.select_related("book", "member").get(id=order_id)
    except Order.DoesNotExist:
        return {"error": f"Order with id {order_id} does not exist"}

    body = f"""
        Hi {order.member.name}!<br />
        "{order.book.title}" book is ready to be picked up. <br />
        Your Reservation ID: {order.reservation.pk} <br />
        Check all your reservations <a href='{reservations_url}' target='_blank'>here</a>
    """

    mailer = Mailer(
        Message(
            subject="Book is ready to be picked up",
            # to=(order.member.email,),
            body=body,
        )
    )
    email_sent = mailer.send()

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
        Message(
            subject="Registration request received",
            # to=env("LIBRARIAN_ADMIN_EMAIL"),
            body=body,
        )
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
        Hi {member.name}! <br />
        Your registration code: {member.registration_code}. <br />
        Please arrive to library to complete registration. <br />
        Don't forget to bring your ID card.
    """

    mailer = Mailer(
        Message(
            subject="Thanks! Your registration request received",
            # to=env("member.email"),
            body=body,
        )
    )

    email_sent = mailer.send()

    return {"sent": email_sent}


@shared_task(name="core/send_password_reset_link_to_member")
def send_password_reset_link_to_member(member_id: int):
    with transaction.atomic():
        try:
            member = Member.objects.select_for_update().get(id=member_id)
            if not member.is_password_reset_token_valid():
                member.set_password_reset_token()
        except Member.DoesNotExist:
            return {"error": f"Member with id {member_id} does not exist"}

    password_reset_url = urljoin(env("PRODUCTION_URL"), f"/reset-password/{member.password_reset_token}")

    body = f"""
        Hi {member.name}! <br />
        You requested password reset recently. <br />
        Please visit that link below to set a new password for your account: <br />
        <a href='{password_reset_url}' target='_blank'>Reset password</a> <br />
        Link expires in 1 hour.
    """

    mailer = Mailer(
        Message(
            subject="Password reset request",
            # to=env("member.email"),
            body=body,
        )
    )

    email_sent = mailer.send()

    return {"sent": email_sent}
