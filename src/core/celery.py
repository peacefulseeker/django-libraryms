import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

from core.conf.environ import env

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery(
    "django_libraryms",
    broker_url=env("CELERY_BROKER_URL", str, default="redis://redis:6379"),
    result_backend=env("CELERY_RESULT_BACKEND", str, default="django-db"),
    task_always_eager=env("CELERY_ALWAYS_EAGER", cast=bool, default=settings.DEBUG),
    enable_utc=False,
    result_extended=True,
    timezone=env("TIME_ZONE"),
    beat_schedule={
        # just for IDE navigation convenience
        "core.tasks.ping_production_website": {
            "task": "core/ping_production_website",  # name of the registered task in celery, not the task path
            "schedule": crontab(minute="*/10"),
        },
    },
)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")


app.autodiscover_tasks(
    packages=[
        "core",
    ]
)
