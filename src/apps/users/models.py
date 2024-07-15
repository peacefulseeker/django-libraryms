import uuid

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


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

    class Meta:
        indexes = [
            models.Index(fields=("uuid",)),
        ]

    def __str__(self) -> str:
        return f"{self.username}"


class Member(User):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.is_member = True
        super(Member, self).save(*args, **kwargs)

    objects = UserRoleManager("is_member")


class Librarian(User):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.is_staff = True
        self.is_librarian = True
        super(Librarian, self).save(*args, **kwargs)

    objects = UserRoleManager("is_librarian")
