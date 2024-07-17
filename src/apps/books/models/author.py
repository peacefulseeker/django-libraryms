from django.db import models

from core.utils.models import TimestampedModel


class Author(TimestampedModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    # TODO: try out db_default instead, truncing year https://docs.djangoproject.com/en/5.0/ref/models/fields/#db-default
    year_of_birth = models.PositiveSmallIntegerField(null=True)
    year_of_death = models.PositiveSmallIntegerField(null=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["first_name", "last_name"],
                name="unique_author_name",
            )
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
