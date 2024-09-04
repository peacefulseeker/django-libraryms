ARG PYTHON_VERSION=3.11-slim-bullseye

from python:${PYTHON_VERSION} as poetry-deps-export
    WORKDIR /

    RUN pip install poetry
    COPY pyproject.toml poetry.lock /
    RUN poetry config virtualenvs.create false
    RUN poetry install --no-root --no-interaction
    RUN poetry export --without-hashes --format=requirements.txt --output requirements.txt

FROM python:${PYTHON_VERSION} as backend-build

    ENV PYTHONDONTWRITEBYTECODE 1
    ENV PYTHONUNBUFFERED 1

    RUN useradd --user-group --system --no-log-init --create-home appuser

    RUN apt-get update && apt-get install -y \
        libpq-dev \
        gcc \
        && rm -rf /var/lib/apt/lists/*

    COPY --from=poetry-deps-export /requirements.txt /
    RUN pip install --no-cache-dir -r requirements.txt

FROM backend-build as app
    WORKDIR /app

    COPY src /app/src

    RUN python src/manage.py collectstatic --no-input

    RUN chown -R appuser .
    USER appuser


FROM app as web
    EXPOSE 8000

    HEALTHCHECK CMD curl -f http://localhost/ --header "Referer: healtcheck.django-libraryms.fly.dev" || exit 1
    CMD python -m gunicorn --bind :8000 --chdir src --workers 2 core.wsgi:application
