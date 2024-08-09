import requests
from celery import shared_task
from sentry_sdk.api import capture_exception

from core.conf.environ import env


@shared_task(name="core/ping_production_website")
def ping_production_website(url=env("PRODUCTION_URL")):
    try:
        response = requests.get(url, headers={"User-Agent": "DjangoLibraryMS/CeleryBeat"})
    except requests.exceptions.RequestException as e:
        capture_exception(e)
        return {"error": str(e)}

    return {
        "url": url,
        "status": response.status_code,
        "response_time": response.elapsed.total_seconds(),
    }
