from django.db import models
from django.utils import timezone


# Taken from https://github.com/audiolion/django-behaviors
class TimestampedModel(models.Model):
    """
    An abstract behavior representing timestamping a model with `created_at` and
    `modified_at` fields.
    """

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        abstract = True

    @property
    def changed(self):
        return True if self.modified_at else False

    def save(self, *args, **kwargs):
        if self.pk:
            self.modified_at = timezone.now()
        return super(TimestampedModel, self).save(*args, **kwargs)
