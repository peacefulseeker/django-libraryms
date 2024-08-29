from dataclasses import dataclass

import sentry_sdk
from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django_ses import SESBackend


@dataclass
class Message:
    subject: str
    body: str
    from_email: str = settings.AWS_SES_FROM_EMAIL
    to: list | tuple = (settings.AWS_SES_FROM_EMAIL,)

    def __post_init__(self):
        if not isinstance(self.to, (list, tuple)):
            raise ValueError("'to' must be a list or tuple")

    def __str__(self):
        return self.subject


class HtmlEmailMessage(EmailMessage):
    content_subtype = "html"


class Mailer:
    def __init__(
        self,
        subject,
        body,
        from_email=settings.AWS_SES_FROM_EMAIL,
        to=(settings.AWS_SES_FROM_EMAIL,),  # list or tuple
        reply_to=("noreply@django-libraryms.fly.dev",),  # list or tuple
        headers={},
    ):
        self.email = HtmlEmailMessage(
            subject=subject,
            body=Mailer.compact_body(body),
            from_email=from_email,
            to=to,
            reply_to=reply_to,
            headers=headers,
        )

    def send(self) -> int:
        """
        The return value will be the number of successfully delivered messages
        (which can be 0 or 1 since it can only send one message).
        """
        return self.email.send()

    @classmethod
    def compact_body(cls, body) -> str:
        "Strips whitespaces before/after and within each body line"

        return "".join([line.strip() for line in body.split("\n")])

    @classmethod
    def send_mass_mail(
        cls, messages: list[Message], fail_silently=False, auth_user=None, auth_password=None, connection=None
    ) -> tuple[int, list[EmailMessage]]:
        """
        Extends Django's send_mass_mail() to support sending mass emails as html by default.
        """
        connection: SESBackend = connection or get_connection(
            username=auth_user,
            password=auth_password,
            fail_silently=fail_silently,
        )
        messages = [
            HtmlEmailMessage(message.subject, cls.compact_body(message.body), message.from_email, message.to, connection=connection) for message in messages
        ]

        emails_sent = connection.send_messages(messages)

        if fail_silently:
            failed_delivery = [m for m in messages if m.extra_headers.get("status", 200) != 200]
            for failed_email in failed_delivery:
                sentry_sdk.capture_message(
                    "Failed to send reminder email",
                    extra={
                        "status": failed_email.extra_headers["status"],
                        "message": failed_email.extra_headers["message"],
                        "reason": failed_email.extra_headers["reason"],
                        "error_message": failed_email.extra_headers["error_message"],
                        "error_code": failed_email.extra_headers["error_code"],
                    },
                )
            # TODO: add failure emailure deliveries for retry in separate periodict task
            # .e.g by saving all context in FailedEmail model

        return emails_sent
