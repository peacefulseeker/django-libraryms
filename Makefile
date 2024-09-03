manage = poetry run python src/manage.py
test = poetry run pytest --capture=fd --verbosity=0
testinparallel = $(test) --numprocesses auto
testwithcoverage = $(test) \
		--cov=apps --cov=core \
		--cov-report=term-missing:skip-covered \
		--cov-fail-under=90

PORT := 7070

server:
	$(manage) runserver $(PORT)

s:
	make server

prodserver:
	poetry run gunicorn core.wsgi:application --chdir src --workers 2 -b localhost:$(PORT) -e DEBUG=false

shell:
	$(manage) shell

sqldebugshell:
	$(manage) debugsqlshell

static:
	$(manage) collectstatic --no-input

build_static:
	make build_frontend
	make static

build_frontend:
	./scripts/build-frontend.sh

build_backend:
	./scripts/build-backend.sh

test:
	$(testinparallel)
	poetry run pytest --dead-fixtures

testwithcoverage:
	$(testwithcoverage)

testwithhtmlcoverage:
	$(testwithcoverage) --cov-report=html:htmlcov

opencoverage:
	open ./htmlcov/index.html

fmt:
	poetry run ruff format src tests
	poetry run ruff check --select I --fix  # sort imports
	poetry run toml-sort pyproject.toml

lint:
	$(manage) makemigrations --check --no-input --dry-run
	poetry run ruff format --check src tests
	poetry run ruff check src tests
	poetry run toml-sort pyproject.toml --check
	poetry run mypy src


# docker
celery_restart:
	docker compose restart celery_beat celery_worker

up:
	docker compose up -d

upbuild:
	docker compose up -d --build

upbuildnocache:
	docker compose up -d --build --force-recreate
