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
    COMPLETED = "C"
    REFUSED = "RF"
    CANCELLED = "X"


class ReservationExtensionStatus(models.TextChoices):
    REQUESTED = "R"
    APPROVED = "A"
    REFUSED = "RF"
    CANCELLED = "X"


# assume that member can cancel the order
# and librarian can refuse and process the order
class OrderStatus(models.TextChoices):
    UNPROCESSED = "U"
    REFUSED = "R"
    IN_QUEUE = "Q"
    MEMBER_CANCELLED = "MC"
    PROCESSED = "P"
