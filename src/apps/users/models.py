import uuid
from django.contrib.auth.models import Group

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class GroupManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(groups__name=self.model.GROUP_NAME)


class User(AbstractUser):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    class Meta:
        indexes = [
            models.Index(fields=("uuid",)),
        ]

    def add_to_group(self, group_name: str):
        group, _ = Group.objects.get_or_create(name=group_name)
        self.groups.add(group)
        print(f"User {self.email} was added to group: ", group_name)


class Member(User):
    GROUP_NAME = "Member"
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        super(Member, self).save(*args, **kwargs)
        self.add_to_group(self.GROUP_NAME)

    objects = GroupManager()


class Librarian(User):
    GROUP_NAME = "Librarian"

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.is_staff = True
        super(Librarian, self).save(*args, **kwargs)
        self.add_to_group(self.GROUP_NAME)

    objects = GroupManager()
