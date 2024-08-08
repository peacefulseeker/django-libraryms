ARG PYTHON_VERSION=3.11-slim-bullseye

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# RUN adduser --system --no-create-home appuser

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app

WORKDIR /app

RUN pip install poetry
COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false
RUN poetry install --only main --no-root --no-interaction

COPY . /app

RUN poetry run python src/manage.py collectstatic --no-input

# RUN chmod +x ./scripts/build.sh
# RUN chmod +x ./entrypoint.sh

EXPOSE 8000

# RUN chown -R appuser .

# USER appuser

# will be rewritten by each of processes
CMD ./entrypoint.sh
