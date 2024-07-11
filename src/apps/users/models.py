import uuid

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class User(AbstractUser):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    is_member = models.BooleanField(default=False)
    is_librarian = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=("uuid",)),
        ]


class MemberManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_member=True)


class Member(User):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.is_member = True
        super(Member, self).save(*args, **kwargs)

    objects = MemberManager()


class LibrarianManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_librarian=True)


class Librarian(User):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.is_staff = True
        self.is_librarian = True
        super(Librarian, self).save(*args, **kwargs)

    objects = LibrarianManager()
