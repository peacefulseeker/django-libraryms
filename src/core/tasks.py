from celery import shared_task

from core.conf.environ import env


@shared_task
def sample_task():
    return "Hello from shared task"


@shared_task
def ping_production_website():
    import requests

    try:
        response = requests.get(env("PRODUCTION_URL"), headers={"User-Agent": "DjangoLibraryMS/CeleryBeat"})
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

    return {
        "status": response.status_code,
        "response_time": response.elapsed.total_seconds(),
    }
