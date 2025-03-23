manage = poetry run python src/manage.py
test = poetry run pytest --capture=fd --verbosity=0
testinparallel = $(test) --numprocesses auto
testwithcoverage = $(test) \
		--cov=apps --cov=core \
		--cov-report=term-missing:skip-covered \
		--cov-fail-under=90

APP_SERVER_PORT := 7070
DATE=$(shell date +%d-%m-%Y)
PG_DUMP_REMOTE="dump-remote-$(DATE).sql"
PG_DUMP_LOCAL="dump-local-$(DATE).sql"
PROD_IMAGE_NAME="django-library-web-prod"
PROD_IMAGE_TAG="latest"

# AUTOLOADS ENV VARIABLES
-include .env
export $(shell sed 's/=.*//' .env)

server:
	$(manage) runserver $(APP_SERVER_PORT)

s:
	make server

prodserver:
	poetry run gunicorn core.wsgi:application --chdir src --workers 2 -b localhost:$(APP_SERVER_PORT) -e DEBUG=false

shell:
	$(manage) shell

sqldebugshell:
	$(manage) debugsqlshell

dbshell:
	$(manage) dbshell

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

testwithcoveragehtml:
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

validate_schema:
	$(manage) spectacular --file schema.yaml --validate

generate_schema:
	$(manage) spectacular --color --file schema.yaml

# DOCKER & COMPPOSE
celery_restart:
	docker compose restart celery_beat celery_worker

up:
	docker compose up -d

# essential for main development
upwebdb:
	docker compose up web db -d

# up all services in compose
upbuild:
	docker compose up -d --build

upbuildnocache:
	docker compose up -d --build --force-recreate

dockerprodbuild:
	docker build . -t ${PROD_IMAGE_NAME}:${PROD_IMAGE_TAG} --no-cache

# NOTE: when loading from .env ENV vars such ALLOWED_HOSTS should NOT contain quotes around the values
# DATABASE_URL is based on the db service in compose and default shared netework
dockerprodrun:
	docker run --name ${PROD_IMAGE_NAME} -d -p 8000:8000 \
		--network django-libraryms_default \
		-e DEBUG=false \
		-e ALLOWED_HOSTS="localhost" \
		-e DATABASE_URL="postgres://postgres:postgres@db:5433/web_libraryms" \
		--env-file=src/core/.env ${PROD_IMAGE_NAME}:${PROD_IMAGE_TAG}

dockerprodexec:
	docker exec -it ${PROD_IMAGE_NAME} /bin/bash

dockerprodlogs:
	docker logs ${PROD_IMAGE_NAME} -f

dockerprodremove:
	docker rm -f ${PROD_IMAGE_NAME}

# POSTGRES(local and remote)
# Proxies connections to a Fly Machine through a WireGuard tunnel.(remote:local)
# autoselects first available machine
pgproxy:
	fly proxy 15432:5432 --app django-libraryms-db

# connect to proxied db
pgconnectremote:
	PGPASSWORD=${PGPASSWORD_REMOTE} psql -h localhost -p 15432 -d django_libraryms -U postgres

# or `manage.py dbshell` will do natively
pgconnectlocal:
	PGPASSWORD=${PGPASSWORD_LOCAL} psql -h localhost -U postgres -d  web_libraryms -p 5433

# Dumps fly db django_libraryms to local file
pgdumpremote:
	PGPASSWORD=${PGPASSWORD_REMOTE} pg_dump -h localhost -p 15432 -U postgres django_libraryms > db/$(PG_DUMP_REMOTE)

# Dumps local db django_libraryms to local file
pgdumplocal:
	PGPASSWORD=${PGPASSWORD_LOCAL} pg_dump -h localhost -p 5433 -U postgres web_libraryms > db/$(PG_DUMP_LOCAL)

# Load local dump to remote(through proxy) fly pg django_libraryms database
# change source to load(PG_DUMP_REMOTE to PG_DUMP_LOCAL)
pgloadremote:
	PGPASSWORD=${PGPASSWORD_REMOTE} psql -h localhost -p 15432 -U postgres django_libraryms < db/$(PG_DUMP_REMOTE)

# Loads local dump to locally running postgres db(web_libraryms)
# change source to load(PG_DUMP_REMOTE to PG_DUMP_LOCAL)
pgloadlocal:
	PGPASSWORD=${PGPASSWORD_LOCAL} psql -h localhost -U postgres -d web_libraryms -p 5433 < db/$(PG_DUMP_LOCAL)
