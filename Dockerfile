ARG NODE_VERSION=20.9.0
ARG PYTHON_VERSION=3.11-slim-bullseye

FROM node:${NODE_VERSION}-slim as frontend

    LABEL fly_launch_runtime="Vite"

    # Vite app lives here
    WORKDIR /app

    # Set production environment
    ENV NODE_ENV="production"

    # Install pnpm
    ARG PNPM_VERSION=9.5.0
    RUN npm install -g pnpm@$PNPM_VERSION

    RUN apt-get update -qq && \
        apt-get install --no-install-recommends -y build-essential node-gyp pkg-config python-is-python3

    # Install node modules
    COPY --link frontend/package.json frontend/pnpm-lock.yaml ./
    RUN pnpm install --frozen-lockfile --prod=false

    COPY --link frontend ./

    # Build application
    RUN pnpm run build

    # Remove development dependencies
    RUN pnpm prune --prod

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
    COPY --from=frontend /app/dist /app/src/core/assets/frontend/
    COPY --from=frontend /app/dist/index.html /app/src/core/templates/vue-index.html

    RUN python src/manage.py collectstatic --no-input

    RUN chown -R appuser .
    USER appuser


FROM app as web
    EXPOSE 8000

    HEALTHCHECK CMD curl -f http://localhost/ --header "Referer: healtcheck.django-libraryms.fly.dev" || exit 1
    CMD python -m gunicorn --bind :8000 --chdir src --workers 2 core.wsgi:application
