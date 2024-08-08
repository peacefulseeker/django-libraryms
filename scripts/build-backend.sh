#! /bin/sh

# Convert static asset files
poetry run python src/manage.py collectstatic --no-input

# Apply any outstanding database migrations
poetry run python src/manage.py migrate
