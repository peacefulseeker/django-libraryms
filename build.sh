#!/usr/bin/env bash
# Exit on error
set -o errexit

# Convert static asset files
python src/manage.py collectstatic --no-input

# Apply any outstanding database migrations
python src/manage.py migrate

cd src/

# python -m gunicorn -b localhost:6004 --env DEBUG=false core.wsgi:application
