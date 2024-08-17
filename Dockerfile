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


FROM python:${PYTHON_VERSION} as backend

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# RUN adduser --system --no-create-home appuser
# RUN useradd -l -M appuser

RUN useradd --user-group --system --no-log-init --create-home appuser

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app

WORKDIR /app

RUN pip install poetry
COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false
# NOTE: that will still installs dev deps because of the poetry following original lock file deps
RUN poetry install --only main --no-root --no-interaction

COPY . /app
COPY --from=frontend /app/dist /app/frontend/dist/
COPY --from=frontend /app/dist/index.html /app/src/core/templates/vue-index.html

RUN python src/manage.py collectstatic --no-input

EXPOSE 8000

RUN chown -R appuser .
USER appuser
# CMD will be rewritten by each of the processes in fly.toml
CMD python -m gunicorn --bind :8000 --chdir src --workers 2 core.wsgi:application
