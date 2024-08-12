import uuid

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRoleManager(UserManager):
    def __init__(self, role_flag):
        super().__init__()
        self.role_flag = role_flag

    def get_queryset(self):
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

    def __str__(self) -> str:
        return f"{self.get_full_name()}"


class UserS(User):
    """
    Since auth.User is already defined, need to use proxy model
    to define "auth" app to custom user model and display
    all auth related models together in admin top
    """

    class Meta:
        proxy = True
        app_label = "auth"
        verbose_name = _("User")
        verbose_name_plural = _("Users")


class Member(User):
    class Meta:
        proxy = True
        app_label = "auth"

    def save(self, *args, **kwargs):
        self.is_member = True
        super(Member, self).save(*args, **kwargs)

    objects = UserRoleManager("is_member")


class Librarian(User):
    class Meta:
        proxy = True
        app_label = "auth"

    def save(self, *args, **kwargs):
        self.is_staff = True
        self.is_librarian = True
        super(Librarian, self).save(*args, **kwargs)

    objects = UserRoleManager("is_librarian")
