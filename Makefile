manage = poetry run python src/manage.py

server:
	$(manage) runserver 7070

shell:
	$(manage) shell

test:
	# TODO: add test coverage
	poetry run pytest
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
