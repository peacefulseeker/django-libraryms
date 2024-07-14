from django.db import models
from django.utils.translation import gettext_lazy as _

from core.utils.models import TimestampedModel


class Language(models.TextChoices):
    LATVIAN = "lv"
    ENGLISH = "en"
    RUSSIAN = "ru"
    GERMAN = "de"
    SPANISH = "es"
    FRENCH = "fr"


# for now keeping models in scope of one app,
# since at the moment don't see them anywhere outside of books app
class Book(TimestampedModel):
    title = models.CharField(max_length=200, unique=True)
    author = models.ForeignKey("Author", on_delete=models.CASCADE)
    language = models.CharField(choices=Language, max_length=2)
    publisher = models.ForeignKey("Publisher", on_delete=models.CASCADE)
    published_at = models.PositiveSmallIntegerField(_("Year of publishing"))
    pages = models.PositiveSmallIntegerField(_("Number of pages"))
    pages_description = models.CharField(_("Extra description for pages"), max_length=100, null=True)
    isbn = models.CharField(max_length=13, verbose_name=_("ISBN"))

    def __str__(self) -> str:
        return f"{self.title}"

    class Meta:
        ordering = ["-modified_at"]


class Author(TimestampedModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
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


class Publisher(TimestampedModel):
    name = models.CharField(max_length=100, unique=True)
    city = models.CharField(max_length=100, null=True)

    def __str__(self) -> str:
        return f"{self.name}"
