ARG PYTHON_VERSION=3.11-slim-bullseye

FROM python:${PYTHON_VERSION} as poetry-deps-export
    WORKDIR /

    ENV POETRY_VERSION=2.1.1

    # Install dependencies first (changes less frequently)
    COPY pyproject.toml poetry.lock /

    # Then install system and Python packages
    RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev \
        build-essential \
        && rm -rf /var/lib/apt/lists/* \
        && pip install --upgrade pip \
        && pip install poetry==${POETRY_VERSION} poetry-plugin-export==1.9.0 \
        && poetry config virtualenvs.create false \
        && poetry install --no-root --no-interaction \
        && poetry export --without-hashes --format=requirements.txt --output requirements.txt

FROM python:${PYTHON_VERSION} as backend-build

    ENV PYTHONDONTWRITEBYTECODE 1
    ENV PYTHONUNBUFFERED 1

    RUN useradd --user-group --system --no-log-init --create-home appuser

    RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev \
        build-essential \
        && rm -rf /var/lib/apt/lists/*

    COPY --from=poetry-deps-export /requirements.txt /
    RUN pip install --no-cache-dir -r requirements.txt

FROM backend-build as app
    WORKDIR /app

    # Copy files and set ownership in one step
    COPY --chown=appuser:appuser src /app/src

    # Run collectstatic as the appuser
    USER appuser
    RUN python src/manage.py collectstatic --no-input

FROM app as web
    EXPOSE 8000

    HEALTHCHECK CMD curl -f http://localhost/ --header "Referer: healthcheck.django-libraryms.fly.dev" || exit 1
    CMD python -m gunicorn --bind :8000 --chdir src --workers 2 core.wsgi:application
