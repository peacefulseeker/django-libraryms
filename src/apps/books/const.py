from django.db import models


class Language(models.TextChoices):
    LATVIAN = "lv"
    ENGLISH = "en"
    RUSSIAN = "ru"
    GERMAN = "de"
    SPANISH = "es"
    FRENCH = "fr"


class ReservationStatus(models.TextChoices):
    RESERVED = "R"
    ISSUED = "I"
    COMPLETED = "C"  # TODO: or returned?
    REFUSED = "RF"
    CANCELLED = "X"


class OrderStatus(models.TextChoices):
    UNPROCESSED = "U"
    REFUSED = "R"
    IN_QUEUE = "Q"
    MEMBER_CANCELLED = "MC"
    PROCESSED = "P"
