from django.conf import settings
from django.core.mail import EmailMessage


class Mailer:
    def __init__(
        self,
        subject,
        body,
        from_email=settings.AWS_SES_FROM_EMAIL,
        to=(settings.AWS_SES_FROM_EMAIL,),  # list or tuple
        reply_to=("noreply@libms.dev",),  # list or tuple
        headers={},
    ):
        self.email = EmailMessage(
            subject=subject,
            body=body,
            from_email=from_email,
            to=to,
            reply_to=reply_to,
            headers=headers,
        )
        self.email.content_subtype = "html"

    def send(self) -> int:
        """
        The return value will be the number of successfully delivered messages
        (which can be 0 or 1 since it can only send one message).
        """
        return self.email.send()
