#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install --upgrade pip
pip install poetry==1.8.3

poetry install

# Convert static asset files
poetry run python src/manage.py collectstatic --no-input

# Apply any outstanding database migrations
poetry run python src/manage.py migrate

# python -m gunicorn -b localhost:6004 --env DEBUG=false core.wsgi:application
