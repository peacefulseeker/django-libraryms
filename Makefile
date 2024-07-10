manage = poetry run python src/manage.py

server:
	$(manage) runserver 7070

shell:
	$(manage) shell

