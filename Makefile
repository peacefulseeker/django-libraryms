manage = poetry run python src/manage.py

server:
	$(manage) runserver 7070

shell:
	$(manage) shell

test:
	# TODO: add test coverage
	poetry run pytest
	poetry run pytest --dead-fixtures

seed_users:
	$(manage) seed_users
