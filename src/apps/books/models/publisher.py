from django.db import models

from core.utils.models import TimestampedModel


class Publisher(TimestampedModel):
    name = models.CharField(max_length=100, unique=True)
    city = models.CharField(max_length=100, null=True)

    def __str__(self) -> str:
        return f"{self.name}"
