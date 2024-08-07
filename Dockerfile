FROM python:3.11-slim-bookworm as base
    # Makefile commands
    RUN apt-get update && apt-get install make

    ENV POETRY_VERSION=1.8.3
    ENV POETRY_VIRTUALENVS_CREATE=false
    ENV POETRY_VIRTUALENVS_IN_PROJECT=false
    ENV PIP_ROOT_USER_ACTION=ignore

    RUN pip install --upgrade pip
    RUN pip install poetry==${POETRY_VERSION}

    COPY pyproject.toml poetry.lock .


FROM base AS poetry-export
    RUN poetry self add poetry-plugin-export@latest
    RUN poetry export -f requirements.txt --output requirements.txt


FROM base as development
    WORKDIR /app

    RUN poetry install

    COPY ./compose/local/start_web /start_web
    RUN chmod +x /start_web

    COPY ./compose/local/start_celery_worker /start_celery_worker
    RUN chmod +x /start_celery_worker

    COPY ./compose/local/start_celery_beat /start_celery_beat
    RUN chmod +x /start_celery_beat

    COPY ./compose/local/start_celery_flower /start_celery_flower
    RUN chmod +x /start_celery_flower
