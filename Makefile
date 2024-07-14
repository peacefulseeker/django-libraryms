manage = poetry run python src/manage.py

server:
	$(manage) runserver 7070

s:
	make server

shell:
	$(manage) shell

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
