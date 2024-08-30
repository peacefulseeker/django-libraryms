import uuid
from typing import Any

from django.contrib import admin
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class InvalidPasswordResetTokenError(Exception):
    pass


class UserRoleManager(UserManager):
    def __init__(self, role_flag: str) -> None:
        super().__init__()
        self.role_flag = role_flag

    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(**{self.role_flag: True})


class User(AbstractUser):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    is_member = models.BooleanField(default=False)
    is_librarian = models.BooleanField(default=False)
    email = models.EmailField(
        _("Email address"),
        unique=True,
        error_messages={
            "unique": _("A user with such email already exists."),
        },
    )

    password_reset_token = models.UUIDField(unique=True, null=True, blank=True, editable=False)
    password_reset_token_created_at = models.DateTimeField(null=True, blank=True)

    def is_password_reset_token_valid(self, raise_exception: bool = False) -> bool | None:
        if not self.password_reset_token or not self.password_reset_token_created_at:
            if raise_exception:
                raise InvalidPasswordResetTokenError("No valid reset token found")
            return False

        expiry_time = self.password_reset_token_created_at + timezone.timedelta(hours=1)
        if timezone.now() > expiry_time:
            if raise_exception:
                raise InvalidPasswordResetTokenError("Token has expired")
            return False

        return True

    def set_password_reset_token(self) -> None:
        """
        Generates a new token for user only in case
        previous token does not exist or expired
        """
        if not self.is_password_reset_token_valid():
            self.password_reset_token = uuid.uuid4()
            self.password_reset_token_created_at = timezone.now()
            self.save()

    def __str__(self) -> str:
        return f"{self.get_full_name()}"


class Member(User):
    class Meta:
        proxy = True

    objects = UserRoleManager("is_member")

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.is_member = True
        super(Member, self).save(*args, **kwargs)

    @property
    @admin.display(
        # description="Code that member will receive upon registration request",
        boolean=False,
    )
    def registration_code(self) -> str:
        """
        Code that will be sent to member upon registration request.
        For simplicity, leveraging existing uuid field,
        which can become essential part of public member profile later on.
        """
        return str(self.uuid.int)[:6]

    @property
    def name(self) -> str:
        return self.first_name or self.username


class Librarian(User):
    class Meta:
        proxy = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.is_staff = True
        self.is_librarian = True
        super(Librarian, self).save(*args, **kwargs)

    objects = UserRoleManager("is_librarian")
