from django.conf import settings
from django.core.mail import EmailMessage


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
        self.email = EmailMessage(
            subject=subject,
            body=self.compact_body(body),
            from_email=from_email,
            to=to,
            reply_to=reply_to,
            headers=headers,
        )
        self.email.content_subtype = "html"

    @staticmethod
    def compact_body(body) -> str:
        "Strips whitespaces before/after and within each body line"

        return "".join([line.strip() for line in body.split("\n")])

    def send(self) -> int:
        """
        The return value will be the number of successfully delivered messages
        (which can be 0 or 1 since it can only send one message).
        """
        return self.email.send()
