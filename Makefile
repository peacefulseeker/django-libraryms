manage = poetry run python src/manage.py
PORT := 7070

server:
	$(manage) runserver $(PORT)

s:
	make server

prod:
	make static
	DEBUG=false poetry run gunicorn core.wsgi:application --chdir src --workers 2 -b localhost:$(PORT)

shell:
	$(manage) shell

static:
	$(manage) collectstatic --no-input

test:
	poetry run pytest --cov=apps --cov=core --cov-report=html:htmlcov --cov-report=term-missing
	poetry run pytest --dead-fixtures

seed_db:
	$(manage) seed_db

fmt:
	poetry run ruff format src tests
	poetry run ruff check --select I --fix  # sort imports
	poetry run toml-sort pyproject.toml

lint:
	$(manage) makemigrations --check --no-input --dry-run
	poetry run ruff format --check src tests
	poetry run ruff check src tests
	poetry run toml-sort pyproject.toml --check


# docker
restart_celery_all:
	docker compose restart celery_flower celery_beat celery_beat

up:
	docker compose up -d

upbuild:
	docker compose up -d --build

upbuildnocache:
	docker compose up -d --build --force-recreate
