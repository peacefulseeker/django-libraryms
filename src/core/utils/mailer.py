import json
import logging
from typing import Any, NamedTuple

import sentry_sdk
from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django_ses import SESBackend
from mypy_boto3_ses import SESClient

logger = logging.getLogger()


class Message(NamedTuple):
    template_name: str
    template_data: dict[str, Any] = {}
    from_email: str = settings.AWS_SES_FROM_EMAIL
    to: list[str] | tuple[str] = (settings.AWS_SES_FROM_EMAIL,)
    reply_to: list[str] | tuple[str] = ("noreply@django-libraryms.fly.dev",)


class HtmlEmailMessage(EmailMessage):
    content_subtype = "html"


class Mailer:
    @classmethod
    def send_templated_email(cls, message: Message, connection: SESBackend = None) -> int:
        """
        Sends templated email using Amazon SES or prints to console if not using SES.
        """

        backend: SESBackend = connection or get_connection()
        if not hasattr(backend, "connection"):
            logger.info(f"Sending '{message.template_name}' email to {message.to}")
            return 1

        num_sent = 0
        new_conn_created = backend.open()
        try:
            ses_client: SESClient = backend.connection
            ses_client.send_templated_email(
                Source=message.from_email,
                Destination={
                    "ToAddresses": message.to,
                },
                ReplyToAddresses=message.reply_to,
                Template=message.template_name,
                TemplateData=json.dumps(message.template_data),
            )
            num_sent += 1
            logger.info(f"Sent '{message.template_name}' email to {message.to}")
        except Exception as exc:
            # TODO: add failure emailure deliveries for retry in separate periodict task
            # .e.g by saving all context in FailedEmail model
            sentry_sdk.capture_exception(exc)

        if new_conn_created:
            backend.close()

        return num_sent

    @classmethod
    def send_mass_templated_email(cls, messages: list[Message]) -> int:
        connection = get_connection()
        num_sent = 0
        for message in messages:
            num_sent += cls.send_templated_email(message, connection)
        return num_sent
