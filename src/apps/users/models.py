import uuid
from django.contrib.auth.models import Group

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    group_name = None

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    class Meta:
        indexes = [
            models.Index(fields=("uuid",)),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.group_name is not None:
            self.add_to_group(self.group_name)

    def add_to_group(self, group_name: str):
        group, _ = Group.objects.get_or_create(name=group_name)
        self.groups.add(group)
        print(f"User {self.email} was added to group: ", group_name)


class Member(User):
    group_name = "Members"

    class Meta:
        proxy = True


class Librarian(User):
    group_name = "Librarians"

    class Meta:
        proxy = True
