from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.utils.models import TimestampedModel

max_year_validator = MaxValueValidator(
    datetime.today().year,
    message="Year of birth cannot be greater than current year",
)


class Author(TimestampedModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    year_of_birth = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[max_year_validator],
    )
    year_of_death = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[max_year_validator],
    )

    class Meta:
        ordering = ["last_name", "first_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["first_name", "last_name"],
                name="unique_author_name",
            )
        ]

    def clean(self) -> None:
        if all([self.year_of_birth, self.year_of_death]):
            if self.year_of_birth > self.year_of_death:
                raise ValidationError(_("Year of birth cannot be greater than year of death"))

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"
