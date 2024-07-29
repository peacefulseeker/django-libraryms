FROM python:3.11-slim-bookworm as base

WORKDIR /app
ENV POETRY_VERSION=1.8.3
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_VIRTUALENVS_IN_PROJECT=false


FROM base AS poetry
RUN pip install --upgrade pip
RUN pip install poetry==${POETRY_VERSION}

COPY pyproject.toml poetry.lock .

RUN poetry export -f requirements.txt --output requirements.txt

FROM base as development
COPY --from=poetry /app/requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
