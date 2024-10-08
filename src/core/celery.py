import os

from celery import Celery
from celery.app.task import Task
from django.conf import settings

from core.conf.environ import env

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

celery = Celery(
    "django_libraryms",
    broker_url=env("CELERY_BROKER_URL", str, default="redis://redis:6379"),
    result_backend=env("CELERY_RESULT_BACKEND", str, default="django-db"),
    task_always_eager=env.bool("CELERY_ALWAYS_EAGER", default=settings.DEBUG),
    enable_utc=False,
    result_extended=True,
    task_store_errors_even_if_ignored=True,
    timezone=env("TIME_ZONE"),
)


@celery.task(bind=True, ignore_result=True)
def debug_task(self: Task) -> None:
    print(f"Request: {self.request!r}")  # pragma: no cover


celery.autodiscover_tasks(
    packages=[
        "core",
        "apps",
    ]
)
