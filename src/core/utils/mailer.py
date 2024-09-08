import json
import logging
from typing import TYPE_CHECKING, Any, NamedTuple

import sentry_sdk
from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django_ses import SESBackend

logger = logging.getLogger()

if TYPE_CHECKING:
    from mypy_boto3_ses import SESClient
    from mypy_boto3_ses.type_defs import SendBulkTemplatedEmailResponseTypeDef


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
    def send_templated_email(cls, message: Message) -> int:
        """
        Sends templated email using Amazon SES or prints to console if not using SES.
        """

        backend: SESBackend = get_connection()
        if not hasattr(backend, "connection"):
            logger.info(f"Sending '{message.template_name}' email to {message.to}")
            return 1

        num_sent = 0
        new_conn_created = backend.open()
        try:
            ses_client: "SESClient" = backend.connection
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
            sentry_sdk.capture_exception(exc)

        if new_conn_created:
            backend.close()

        return num_sent

    @classmethod
    def send_bulk_templated_email(cls, messages: list[Message], template: str) -> int:
        backend: SESBackend = get_connection()
        if not hasattr(backend, "connection"):
            logger.info(f"Sending '{template}' email to [{[', '.join(message.to) for message in messages]}]")
            return len(messages)

        num_sent = 0
        new_conn_created = backend.open()
        try:
            ses_client: SESClient = backend.connection
            response: "SendBulkTemplatedEmailResponseTypeDef" = ses_client.send_bulk_templated_email(
                Source=Message._field_defaults["from_email"],
                ReplyToAddresses=Message._field_defaults["reply_to"],
                DefaultTemplateData="{}",
                Template=template,
                Destinations=[
                    {
                        "Destination": {
                            "ToAddresses": message.to,
                        },
                        "ReplacementTemplateData": json.dumps(message.template_data),
                    }
                    for message in messages
                ],
            )

            for message in response["Status"]:
                if message["Status"] == "Success":
                    num_sent += 1
                else:
                    sentry_sdk.capture_message(
                        f"Failed to deliver email. Status: {message['Status']}, Error: {message['Error']}",
                        level="error",
                    )
        except Exception as exc:
            sentry_sdk.capture_exception(exc)

        if new_conn_created:
            backend.close()

        return num_sent
